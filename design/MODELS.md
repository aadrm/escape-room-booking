``` mermaid
classDiagram

    Coupon --|> CartCoupon
    CartCoupon  "0..*" <--> "1" Cart :Is in
    Cart "1" --|> ProductGroup
    ProductGroup "0..*" --|> BaseProduct

    namespace appointments{
        class Slot
        class Schedule
        class Appointments

    }
    Slot "0..n" --|> Schedule
    Schedule "1" --|> Appointments
    Slot "0..n" --|> Shift
    class Room {
        name: string
        description: string
        is_active: bool
        theme_colour: char
    }

    class Schedule {
        start_date: date
        end_date: date
        days_of_week: days
        start_time: time
        duration_minutes: int
        buffer_minutes: int
        repeat_times: int
        room: Room
    }

    class Slot {
        start: datetime
        duration: int
        buffer: int
        is_enabled: bool
        /appointment_end: datetime
        /block_end: datetime
        /is_available
        /is_available_to_staff

        is_booked()
        is_blocked_by_buffer()
        is_future_of_buffer()
        get_adjacent_slots()
        is_parallel_to_taken_slot()
    }

    class BaseProduct {
        --
    }

    class Cart {
        --
    }

    class CartItem {
        addItemToCart()
    }

    class AppointmentProductGroup {
        --
    }

    class VoucherProduct {
        --
    }

    class Coupon {
        --
    }

    class CartCoupon {
        --
    }

    class ProductGroup {
        --
    }

    class Appointments {
        --
    }

    class Shift {
        - Date
    }
```

