-- ============================================================
-- SIGVE INTECAP - PostgreSQL Schema V1
-- Fecha: 2026-08-10
-- Alcance:
--   - Usuarios y roles
--   - Vehículos
--   - Solicitudes/comisiones
--   - Recorridos / bitácora
--   - Cupones y cargas de combustible
--   - Mantenimiento, servicios y piezas
--
-- IMPORTANTE:
--   Este esquema contiene únicamente requerimientos confirmados
--   o decisiones técnicas necesarias para que el modelo funcione.
--   Los puntos pendientes están documentados con COMMENT.
-- ============================================================

BEGIN;

-- ------------------------------------------------------------
-- Función genérica para updated_at
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- ============================================================
-- 1. ROLES
-- ============================================================
CREATE TABLE roles (
    id          SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code        VARCHAR(30) NOT NULL UNIQUE,
    name        VARCHAR(50) NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO roles (code, name)
VALUES
    ('ADMINISTRATION', 'Administración'),
    ('COLLABORATOR', 'Colaborador');

-- ============================================================
-- 2. USERS
-- ============================================================
CREATE TABLE users (
    id                   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    role_id              SMALLINT NOT NULL,
    full_name            VARCHAR(150) NOT NULL,
    institutional_email  VARCHAR(254) NOT NULL,
    password_hash        TEXT NOT NULL,
    position             VARCHAR(100) NOT NULL,
    area_department      VARCHAR(150) NOT NULL,
    phone                VARCHAR(30) NOT NULL,
    is_active            BOOLEAN NOT NULL DEFAULT TRUE,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_users_role
        FOREIGN KEY (role_id)
        REFERENCES roles(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE UNIQUE INDEX uq_users_institutional_email_ci
    ON users (LOWER(institutional_email));

CREATE INDEX idx_users_role_id
    ON users (role_id);

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- 3. VEHICLES
-- ============================================================
CREATE TABLE vehicles (
    id                    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    inventory_code        VARCHAR(50) NOT NULL,
    license_plate         VARCHAR(20) NOT NULL,
    brand                 VARCHAR(80) NOT NULL,
    model                 VARCHAR(80) NOT NULL,
    year                  SMALLINT NOT NULL,
    vehicle_type          VARCHAR(80) NOT NULL,
    fuel_type             VARCHAR(30) NOT NULL,
    current_odometer_km   NUMERIC(12,1) NOT NULL DEFAULT 0,
    tank_capacity_gal     NUMERIC(8,3),
    is_active             BOOLEAN NOT NULL DEFAULT TRUE,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_vehicles_year
        CHECK (year >= 1900),

    CONSTRAINT ck_vehicles_odometer
        CHECK (current_odometer_km >= 0),

    CONSTRAINT ck_vehicles_tank_capacity
        CHECK (tank_capacity_gal IS NULL OR tank_capacity_gal > 0)
);

CREATE UNIQUE INDEX uq_vehicles_inventory_code_ci
    ON vehicles (LOWER(inventory_code));

CREATE UNIQUE INDEX uq_vehicles_license_plate_ci
    ON vehicles (LOWER(license_plate));

CREATE TRIGGER trg_vehicles_updated_at
BEFORE UPDATE ON vehicles
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

COMMENT ON COLUMN vehicles.tank_capacity_gal IS
'PENDIENTE DE CONFIRMACIÓN: capacidad del tanque en galones. Se deja nullable para soportar el cálculo futuro de combustible restante sin inventar valores.';

COMMENT ON TABLE vehicles IS
'Cilindraje/C.C. no se agregan todavía porque falta confirmar si representan el mismo dato o datos diferentes.';

-- ============================================================
-- 4. COMMISSION STATUSES
-- ============================================================
CREATE TABLE commission_statuses (
    id          SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code        VARCHAR(30) NOT NULL UNIQUE,
    name        VARCHAR(50) NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Estados confirmados por el flujo actual.
-- No se agrega FINALIZADA/COMPLETADA hasta confirmar el nombre
-- y comportamiento definitivo.
INSERT INTO commission_statuses (code, name)
VALUES
    ('PENDING', 'Pendiente'),
    ('APPROVED', 'Aprobada'),
    ('REJECTED', 'Rechazada'),
    ('CANCELLED', 'Cancelada');

-- ============================================================
-- 5. COMMISSIONS
-- ============================================================
CREATE TABLE commissions (
    id                    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    requester_user_id     BIGINT NOT NULL,
    vehicle_id            BIGINT,
    status_id             SMALLINT NOT NULL,
    scheduled_start_at    TIMESTAMPTZ NOT NULL,
    scheduled_end_at      TIMESTAMPTZ NOT NULL,
    reviewed_by_user_id   BIGINT,
    reviewed_at           TIMESTAMPTZ,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_commissions_requester
        FOREIGN KEY (requester_user_id)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_commissions_vehicle
        FOREIGN KEY (vehicle_id)
        REFERENCES vehicles(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_commissions_status
        FOREIGN KEY (status_id)
        REFERENCES commission_statuses(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_commissions_reviewer
        FOREIGN KEY (reviewed_by_user_id)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT ck_commissions_schedule
        CHECK (scheduled_end_at > scheduled_start_at)
);

CREATE INDEX idx_commissions_requester
    ON commissions (requester_user_id);

CREATE INDEX idx_commissions_vehicle_schedule
    ON commissions (vehicle_id, scheduled_start_at, scheduled_end_at)
    WHERE vehicle_id IS NOT NULL;

CREATE INDEX idx_commissions_status
    ON commissions (status_id);

CREATE TRIGGER trg_commissions_updated_at
BEFORE UPDATE ON commissions
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

COMMENT ON TABLE commissions IS
'Las comisiones rechazadas o canceladas permanecen almacenadas. No deben representarse mediante DELETE físico.';

-- ------------------------------------------------------------
-- Regla V1: evitar traslape de un mismo vehículo entre
-- comisiones APROBADAS.
--
-- Se usa advisory lock por vehicle_id para evitar condiciones
-- de carrera entre solicitudes concurrentes.
--
-- Si posteriormente se agregan estados como EN_CURSO que
-- también deban bloquear el vehículo, esta función deberá
-- ampliarse.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION prevent_approved_vehicle_overlap()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    new_status_code VARCHAR(30);
BEGIN
    IF NEW.vehicle_id IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT code
      INTO new_status_code
      FROM commission_statuses
     WHERE id = NEW.status_id;

    IF new_status_code <> 'APPROVED' THEN
        RETURN NEW;
    END IF;

    -- Serializa validaciones concurrentes para el mismo vehículo.
    PERFORM pg_advisory_xact_lock(NEW.vehicle_id);

    IF EXISTS (
        SELECT 1
          FROM commissions c
          JOIN commission_statuses cs
            ON cs.id = c.status_id
         WHERE c.vehicle_id = NEW.vehicle_id
           AND c.id <> COALESCE(NEW.id, 0)
           AND cs.code = 'APPROVED'
           AND tstzrange(
                   c.scheduled_start_at,
                   c.scheduled_end_at,
                   '[)'
               )
               &&
               tstzrange(
                   NEW.scheduled_start_at,
                   NEW.scheduled_end_at,
                   '[)'
               )
    ) THEN
        RAISE EXCEPTION
            'El vehículo % ya está asignado a otra comisión aprobada dentro del intervalo solicitado.',
            NEW.vehicle_id
            USING ERRCODE = '23P01';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_commissions_prevent_vehicle_overlap
BEFORE INSERT OR UPDATE OF vehicle_id, status_id, scheduled_start_at, scheduled_end_at
ON commissions
FOR EACH ROW
EXECUTE FUNCTION prevent_approved_vehicle_overlap();

-- ============================================================
-- 6. TRIPS / BITÁCORA
-- ============================================================
CREATE TABLE trips (
    id                    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    commission_id         BIGINT NOT NULL,
    driver_user_id        BIGINT NOT NULL,
    sequence_number       SMALLINT NOT NULL,
    trip_date             DATE NOT NULL,
    origin                VARCHAR(200) NOT NULL,
    destination           VARCHAR(200) NOT NULL,
    odometer_start_km     NUMERIC(12,1) NOT NULL,
    odometer_end_km       NUMERIC(12,1) NOT NULL,
    distance_km           NUMERIC(12,1)
                          GENERATED ALWAYS AS
                          (odometer_end_km - odometer_start_km) STORED,
    tank_balance_percent  NUMERIC(5,2),
    road_type             CHAR(1) NOT NULL,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_trips_commission
        FOREIGN KEY (commission_id)
        REFERENCES commissions(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_trips_driver
        FOREIGN KEY (driver_user_id)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_trips_commission_sequence
        UNIQUE (commission_id, sequence_number),

    CONSTRAINT ck_trips_sequence
        CHECK (sequence_number > 0),

    CONSTRAINT ck_trips_odometer_start
        CHECK (odometer_start_km >= 0),

    CONSTRAINT ck_trips_odometer_order
        CHECK (odometer_end_km >= odometer_start_km),

    CONSTRAINT ck_trips_tank_balance
        CHECK (
            tank_balance_percent IS NULL
            OR tank_balance_percent BETWEEN 0 AND 100
        ),

    CONSTRAINT ck_trips_road_type
        CHECK (road_type IN ('A', 'T'))
);

CREATE INDEX idx_trips_commission
    ON trips (commission_id);

CREATE INDEX idx_trips_driver
    ON trips (driver_user_id);

CREATE INDEX idx_trips_date
    ON trips (trip_date);

COMMENT ON COLUMN trips.road_type IS
'A = Asfalto, T = Tierra.';

COMMENT ON COLUMN trips.tank_balance_percent IS
'Porcentaje estimado de combustible restante. La equivalencia exacta del valor E del formato actual sigue pendiente de confirmación.';

-- ============================================================
-- 7. FUEL COUPONS
-- ============================================================
CREATE TABLE fuel_coupons (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    coupon_number  VARCHAR(50) NOT NULL UNIQUE,
    face_value_q   NUMERIC(10,2) NOT NULL DEFAULT 100.00,
    coupon_date    DATE,
    gas_station    VARCHAR(150),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_fuel_coupons_face_value
        CHECK (face_value_q > 0)
);

COMMENT ON COLUMN fuel_coupons.face_value_q IS
'Actualmente los cupones son de Q100. No se restringe a exactamente Q100 para no bloquear un cambio institucional futuro.';

-- ============================================================
-- 8. COMMISSION COUPONS
-- ============================================================
CREATE TABLE commission_coupons (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    commission_id  BIGINT NOT NULL,
    coupon_id      BIGINT NOT NULL,
    assigned_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    used_at        TIMESTAMPTZ,
    returned_at    TIMESTAMPTZ,

    CONSTRAINT fk_commission_coupons_commission
        FOREIGN KEY (commission_id)
        REFERENCES commissions(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_commission_coupons_coupon
        FOREIGN KEY (coupon_id)
        REFERENCES fuel_coupons(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT ck_commission_coupons_not_used_and_returned
        CHECK (NOT (used_at IS NOT NULL AND returned_at IS NOT NULL)),

    CONSTRAINT ck_commission_coupons_used_after_assignment
        CHECK (used_at IS NULL OR used_at >= assigned_at),

    CONSTRAINT ck_commission_coupons_returned_after_assignment
        CHECK (returned_at IS NULL OR returned_at >= assigned_at)
);

CREATE INDEX idx_commission_coupons_commission
    ON commission_coupons (commission_id);

CREATE INDEX idx_commission_coupons_coupon
    ON commission_coupons (coupon_id);

-- Un cupón no puede estar asignado simultáneamente a dos
-- comisiones. Si fue devuelto, puede volver a asignarse.
-- Si fue usado, returned_at queda NULL, por lo que tampoco
-- podrá volver a utilizarse.
CREATE UNIQUE INDEX uq_commission_coupons_active_coupon
    ON commission_coupons (coupon_id)
    WHERE returned_at IS NULL;

COMMENT ON TABLE commission_coupons IS
'Cuando un cupón se devuelve, la relación histórica se conserva con returned_at, aunque funcionalmente deje de mostrarse como asignado a la comisión.';

-- ============================================================
-- 9. FUEL LOADS
-- ============================================================
CREATE TABLE fuel_loads (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    commission_id  BIGINT NOT NULL,
    loaded_at      TIMESTAMPTZ NOT NULL,
    gas_station    VARCHAR(150) NOT NULL,
    gallons        NUMERIC(10,3) NOT NULL,
    amount_q       NUMERIC(10,2) NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_fuel_loads_commission
        FOREIGN KEY (commission_id)
        REFERENCES commissions(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT ck_fuel_loads_gallons
        CHECK (gallons > 0),

    CONSTRAINT ck_fuel_loads_amount
        CHECK (amount_q > 0)
);

CREATE INDEX idx_fuel_loads_commission
    ON fuel_loads (commission_id);

CREATE INDEX idx_fuel_loads_loaded_at
    ON fuel_loads (loaded_at);

COMMENT ON TABLE fuel_loads IS
'Separa el dinero/cupones asignados del combustible realmente cargado. Permite calcular galones y gasto para el dashboard.';

-- ============================================================
-- 10. MAINTENANCE EVENTS
-- ============================================================
CREATE TABLE maintenance_events (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vehicle_id        BIGINT NOT NULL,
    maintenance_type  VARCHAR(20) NOT NULL,
    maintenance_date  DATE NOT NULL,
    odometer_km       NUMERIC(12,1),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_maintenance_events_vehicle
        FOREIGN KEY (vehicle_id)
        REFERENCES vehicles(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT ck_maintenance_events_type
        CHECK (maintenance_type IN ('PREVENTIVO', 'CORRECTIVO')),

    CONSTRAINT ck_maintenance_events_odometer
        CHECK (odometer_km IS NULL OR odometer_km >= 0)
);

CREATE INDEX idx_maintenance_events_vehicle_date
    ON maintenance_events (vehicle_id, maintenance_date);

-- ============================================================
-- 11. SERVICE TYPES
-- ============================================================
CREATE TABLE service_types (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name           VARCHAR(150) NOT NULL UNIQUE,
    interval_km    NUMERIC(12,1),
    interval_days  INTEGER,
    is_active      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_service_types_interval_km
        CHECK (interval_km IS NULL OR interval_km > 0),

    CONSTRAINT ck_service_types_interval_days
        CHECK (interval_days IS NULL OR interval_days > 0)
);

COMMENT ON TABLE service_types IS
'PENDIENTE DE CONFIRMACIÓN: determinar si la periodicidad de servicios se controla por kilometraje, tiempo o ambos. La V1 soporta las tres posibilidades sin obligar ninguna.';

-- ============================================================
-- 12. MAINTENANCE EVENT SERVICES
-- ============================================================
CREATE TABLE maintenance_event_services (
    maintenance_event_id  BIGINT NOT NULL,
    service_type_id       BIGINT NOT NULL,

    PRIMARY KEY (maintenance_event_id, service_type_id),

    CONSTRAINT fk_maintenance_event_services_event
        FOREIGN KEY (maintenance_event_id)
        REFERENCES maintenance_events(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_maintenance_event_services_service
        FOREIGN KEY (service_type_id)
        REFERENCES service_types(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE INDEX idx_maintenance_event_services_service
    ON maintenance_event_services (service_type_id);

-- ============================================================
-- 13. MAINTENANCE PARTS
-- ============================================================
CREATE TABLE maintenance_parts (
    id                    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    maintenance_event_id  BIGINT NOT NULL,
    part_name             VARCHAR(150) NOT NULL,
    quantity              INTEGER NOT NULL DEFAULT 1,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_maintenance_parts_event
        FOREIGN KEY (maintenance_event_id)
        REFERENCES maintenance_events(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT ck_maintenance_parts_quantity
        CHECK (quantity > 0)
);

CREATE INDEX idx_maintenance_parts_event
    ON maintenance_parts (maintenance_event_id);

COMMIT;
