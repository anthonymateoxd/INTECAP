class RoleNotFoundError(Exception):
    pass


class EmailAlreadyRegisteredError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass


class VehicleNotFoundError(Exception):
    pass


class InventoryCodeAlreadyRegisteredError(Exception):
    pass


class LicensePlateAlreadyRegisteredError(Exception):
    pass


class CommissionStatusNotFoundError(Exception):
    pass


class VehicleInactiveError(Exception):
    pass

class CommissionNotFoundError(Exception):
    pass


class CommissionScheduleConflictError(Exception):
    pass


class CommissionCancellationNotAllowedError(Exception):
    pass


class TripCommissionNotApprovedError(Exception):
    pass


class TripDateOutsideCommissionError(Exception):
    pass


class TripDriverNotFoundError(Exception):
    pass


class TripInvalidOdometerError(Exception):
    pass


class TripNotFoundError(Exception):
    pass


class TripEditNotAllowedError(Exception):
    pass


class TripAlreadyDeletedError(Exception):
    pass


class FuelCouponNotFoundError(Exception):
    pass


class FuelCouponNumberAlreadyExistsError(Exception):
    pass


class FuelLoadNotFoundError(Exception):
    pass


class CommissionCouponNotFoundError(Exception):
    pass


class InsufficientFuelCouponsError(Exception):
    pass


class FuelOperationNotAllowedError(Exception):
    pass

class FuelCouponAlreadyAssignedError(Exception):
    pass


class FuelCommissionNotApprovedError(Exception):
    pass


class FuelCouponStateConflictError(Exception):
    pass


class MaintenanceEventNotFoundError(Exception):
    pass


class ServiceTypeNotFoundError(Exception):
    pass


class ServiceTypeNameAlreadyExistsError(Exception):
    pass


class MaintenanceOperationNotAllowedError(Exception):
    pass


class ServiceTypeInactiveError(Exception):
    pass

class MaintenanceEventAlreadyDeletedError(Exception):
    pass

class ReportOperationNotAllowedError(Exception):
    pass
