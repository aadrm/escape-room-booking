``` mermaid
classDiagram

    namespace Appointments {
        class Slot
        class Schedule
        class Room
    }
    class CartItem


    Slot "0..n" -- "0..1" Schedule
    Slot "0..n" -- "1" Room
    Slot "0..1" -- "0..1" CartItem

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

        +get_slots()
        -_delete_related_slots()
    }

    class Slot {
        start: datetime
        duration: int
        buffer: int
        is_enabled: bool
        /appointment_end: datetime
        /block_end: datetime
        +is_available()
        +is_available_to_staff()

        +is_booked()
        +is_affected_by_buffer()
        +is_future_of_buffer()
        +get_adjacent_slots()
        +is_parallel_to_taken_slot()
    }

```