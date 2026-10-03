"""
This is a Hotel Manager Console application.
Classes for storing data: Room, RoomType, Booking
Main class with business logic included: Hotel

With this app you can create rooms in a hotel,
create bookings in the available rooms,
and cancel bookings.

Validation implemented in:
    - Room creation
    - Booking creation
    - Booking cancellation

Test cases cover the main logic and validations.

To run the program: python booking.py
To run the tests: python -m unittest booking

Author: Balazs Kiss
"""


import unittest
from dataclasses import dataclass
from datetime import date
from enum import Enum


class RoomType(Enum):
    SINGLE = "single"
    DOUBLE = "double"
    TWIN = "twin"
    SUITE = "suite"


@dataclass
class Room:
    number: int
    price: int
    room_type: RoomType

    def __post_init__(self):
        if self.number <= 0:
            raise ValueError("Number has to be a positive number")
        if self.price <= 0:
            raise ValueError("Price has to be a positive number")


@dataclass
class Booking:
    booking_id: int
    room: Room
    guest: str
    start: date
    end: date

    def __post_init__(self):
        if not self.room:
            raise ValueError("Room is required")
        if self.nights <= 0:
            raise ValueError("Invalid date range")
        if not self.guest:
            raise ValueError("Guest is required")

    @property
    def nights(self) -> int:
        return (self.end - self.start).days

    @property
    def total_price(self) -> int:
        return self.nights * self.room.price


class BookingError(Exception):
    pass


class Hotel:
    def __init__(self):
        self.rooms: dict[int, Room] = {}
        self.bookings: dict[int, Booking] = {}
        self.next_booking_id = 1

    def add_room(self, room: Room) -> None:
        if room.number in self.rooms:
            raise BookingError("A room with this number already exists")
        self.rooms[room.number] = room

    def _is_available(self, room_number: int, start: date, end: date) -> bool:
        for booking in self.bookings.values():
            if (
                booking.room.number == room_number
                and booking.start < end
                and booking.end > start
            ):
                return False
        return True

    def create_booking(
        self, room_number: int, guest: str, start: date, end: date
    ) -> Booking:
        if room_number not in self.rooms:
            raise BookingError("A room with this number does not exist")

        booking = Booking(
            booking_id=self.next_booking_id,
            room=self.rooms[room_number],
            guest=guest,
            start=start,
            end=end,
        )
        if not self._is_available(room_number, start, end):
            raise BookingError("The room is unavailable in this date range")

        self.bookings[self.next_booking_id] = booking
        self.next_booking_id += 1

        return booking

    def cancel_booking(self, booking_id: int) -> Booking:
        if booking_id not in self.bookings:
            raise BookingError("A booking with this id does not exist")

        return self.bookings.pop(booking_id)

    def available_rooms(self, start: date, end: date) -> list[Room]:
        if end <= start:
            raise ValueError("Invalid date range")
        return [
            room
            for room in self.rooms.values()
            if self._is_available(room_number=room.number, start=start, end=end)
        ]


TEST_MONTH = (2026, 11)
MENU = ("- 1: Add Room\n"
        "- 2: Available Rooms\n"
        "- 3: Create Booking\n"
        "- 4: Cancel Booking\n"
        "- 5: Exit")


def day(d: int) -> date:
    return date(*TEST_MONTH, d)


def make_test_hotel() -> Hotel:
    hotel = Hotel()
    hotel.add_room(Room(number=101, price=20000, room_type=RoomType.SINGLE))
    hotel.add_room(Room(number=102, price=30000, room_type=RoomType.DOUBLE))
    hotel.add_room(Room(number=103, price=30000, room_type=RoomType.TWIN))
    hotel.add_room(Room(number=201, price=60000, room_type=RoomType.SUITE))
    return hotel


def read_int(message: str) -> int:
    text = input(message).strip()
    try:
        return int(text)
    except ValueError:
        raise ValueError(f"{text!r} is not a whole number") from None


def handle_add_room(hotel: Hotel) -> None:
    number = read_int("Room number: ")
    price = read_int("Price ($): ")
    room_type = input("Type (Single, Double, Twin, Suite): ").strip().lower()
    room = Room(number=number, price=price, room_type=RoomType(room_type))
    hotel.add_room(room)
    print("Room added!")


def list_available_rooms(hotel: Hotel) -> None:
    start = date.fromisoformat(input("Start date (YYYY-MM-DD): "))
    end = date.fromisoformat(input("End date (YYYY-MM-DD): "))
    available = hotel.available_rooms(start=start, end=end)
    if not available:
        print("No available rooms")
    else:
        print("Available rooms:")
    for room in available:
        print(
            f"Room #{room.number} | Price: ${room.price}"
            f" | Type: {room.room_type.value.capitalize()}"
        )


def handle_create_booking(hotel: Hotel) -> None:
    room_number = read_int("Room number: ")
    guest = input("Guest: ").strip()
    start = date.fromisoformat(input("Start date (YYYY-MM-DD): "))
    end = date.fromisoformat(input("End date (YYYY-MM-DD): "))
    booking = hotel.create_booking(
        room_number=room_number, guest=guest, start=start, end=end
    )
    print("Booking successful:")
    print(f"Booking #{booking.booking_id}")
    print(f"Room #{booking.room.number}")
    print(f"{booking.nights} nights")
    print(f"Total price: ${booking.total_price}")


def handle_cancel_booking(hotel: Hotel) -> None:
    booking_id = read_int("Booking id: ")
    booking = hotel.cancel_booking(booking_id=booking_id)
    print("Cancellation successful:")
    print(f"Booking #{booking.booking_id}")
    print(f"Guest: {booking.guest}")


class TestHotel(unittest.TestCase):
    def setUp(self):
        self.hotel = make_test_hotel()

    def test_create_room_invalid_numbers(self):
        for number in [-6, -1, 0]:
            with self.subTest(number=number):
                with self.assertRaisesRegex(ValueError, "Number"):
                    Room(number=number, price=100, room_type=RoomType.SINGLE)

    def test_create_room_invalid_price(self):
        for price in [-6000, -1, 0]:
            with self.subTest(price=price):
                with self.assertRaisesRegex(ValueError, "Price"):
                    Room(number=100, price=price, room_type=RoomType.SINGLE)

    def test_create_room_success(self):
        room = Room(number=101, price=20000, room_type=RoomType.SINGLE)
        self.assertEqual(room.number, 101)
        self.assertEqual(room.price, 20000)
        self.assertEqual(room.room_type, RoomType.SINGLE)

    def test_create_room_minimum_valid_values(self):
        room = Room(number=1, price=1, room_type=RoomType.SINGLE)
        self.assertEqual(room.number, 1)
        self.assertEqual(room.price, 1)

    def test_create_booking_missing_room(self):
        with self.assertRaisesRegex(ValueError, "Room"):
            Booking(booking_id=1, room=None, guest="John Doe", start=day(1), end=day(3))

    def test_create_booking_missing_guest(self):
        for guest in [None, ""]:
            with self.subTest(guest=guest):
                with self.assertRaisesRegex(ValueError, "Guest"):
                    Booking(
                        booking_id=1,
                        room=self.hotel.rooms[101],
                        guest=guest,
                        start=day(1),
                        end=day(3),
                    )

    def test_create_booking_invalid_dates(self):
        cases = {
            "end before start": (day(3), day(1)),
            "same day": (day(3), day(3)),
        }
        for name, (start, end) in cases.items():
            with self.subTest(name):
                with self.assertRaisesRegex(ValueError, "date range"):
                    Booking(
                        booking_id=1,
                        room=self.hotel.rooms[101],
                        guest="John Doe",
                        start=start,
                        end=end,
                    )

    def test_booking_model_success(self):
        room = Room(number=101, price=20000, room_type=RoomType.SINGLE)
        booking = Booking(
            booking_id=1, room=room, guest="John Doe", start=day(1), end=day(3)
        )
        self.assertEqual(booking.booking_id, 1)
        self.assertEqual(booking.room, room)
        self.assertEqual(booking.guest, "John Doe")
        self.assertEqual(booking.start, day(1))
        self.assertEqual(booking.end, day(3))
        self.assertEqual(booking.nights, 2)
        self.assertEqual(booking.total_price, 40000)

    def test_add_room_success(self):
        room = Room(number=301, price=45000, room_type=RoomType.DOUBLE)
        self.hotel.add_room(room)
        self.assertIs(self.hotel.rooms[301], room)

    def test_add_room_duplicate_number(self):
        duplicate = Room(number=101, price=25000, room_type=RoomType.DOUBLE)
        with self.assertRaises(BookingError):
            self.hotel.add_room(duplicate)

    def test_create_booking_success(self):
        booking = self.hotel.create_booking(101, "John Doe", day(1), day(3))
        self.assertIs(self.hotel.bookings[booking.booking_id], booking)
        self.assertEqual(booking.total_price, 40000)

    def test_booking_ids_increase(self):
        first = self.hotel.create_booking(101, "John Doe", day(1), day(3))
        second = self.hotel.create_booking(102, "Jane Doe", day(1), day(3))
        self.assertEqual(second.booking_id, first.booking_id + 1)

    def test_create_booking_nonexistent_room(self):
        with self.assertRaises(BookingError):
            self.hotel.create_booking(999, "John Doe", day(1), day(3))

    def test_create_booking_invalid_dates_not_stored(self):
        with self.assertRaises(ValueError):
            self.hotel.create_booking(101, "John Doe", day(5), day(3))
        self.assertEqual(self.hotel.bookings, {})
        self.assertEqual(self.hotel.next_booking_id, 1)

    def test_overlapping_booking_rejected(self):
        self.hotel.create_booking(101, "John Doe", day(5), day(10))
        cases = {
            "fully inside": (day(6), day(8)),
            "overlaps start": (day(3), day(6)),
            "overlaps end": (day(9), day(12)),
            "contains existing": (day(4), day(11)),
            "identical": (day(5), day(10)),
        }
        for name, (start, end) in cases.items():
            with self.subTest(name):
                with self.assertRaises(BookingError):
                    self.hotel.create_booking(101, "Jane Doe", start, end)

    def test_back_to_back_bookings_allowed(self):
        self.hotel.create_booking(101, "John Doe", day(5), day(10))
        after = self.hotel.create_booking(101, "Jane Doe", day(10), day(12))
        before = self.hotel.create_booking(101, "Max Mustermann", day(3), day(5))
        self.assertIn(after.booking_id, self.hotel.bookings)
        self.assertIn(before.booking_id, self.hotel.bookings)

    def test_same_period_other_room_allowed(self):
        self.hotel.create_booking(101, "John Doe", day(5), day(10))
        booking = self.hotel.create_booking(102, "Jane Doe", day(5), day(10))
        self.assertIn(booking.booking_id, self.hotel.bookings)

    def test_cancel_booking_success(self):
        booking = self.hotel.create_booking(101, "John Doe", day(5), day(10))
        cancelled = self.hotel.cancel_booking(booking.booking_id)
        self.assertIs(cancelled, booking)
        self.assertNotIn(booking.booking_id, self.hotel.bookings)

    def test_cancelled_period_can_be_rebooked(self):
        booking = self.hotel.create_booking(101, "John Doe", day(5), day(10))
        self.hotel.cancel_booking(booking.booking_id)
        rebooked = self.hotel.create_booking(101, "Jane Doe", day(5), day(10))
        self.assertIn(rebooked.booking_id, self.hotel.bookings)

    def test_cancel_nonexistent_booking(self):
        with self.assertRaises(BookingError):
            self.hotel.cancel_booking(999)

    def test_available_rooms_excludes_booked(self):
        self.hotel.create_booking(101, "John Doe", day(5), day(10))
        rooms = self.hotel.available_rooms(day(6), day(8))
        numbers = {room.number for room in rooms}
        self.assertEqual(numbers, {102, 103, 201})

    def test_available_rooms_after_checkout(self):
        self.hotel.create_booking(101, "John Doe", day(5), day(10))
        rooms = self.hotel.available_rooms(day(10), day(12))
        numbers = {room.number for room in rooms}
        self.assertIn(101, numbers)

    def test_available_rooms_invalid_range(self):
        with self.assertRaises(ValueError):
            self.hotel.available_rooms(day(5), day(5))


if __name__ == "__main__":
    hotel = make_test_hotel()
    print("---HOTEL MANAGER---")
    while True:
        print(MENU)
        try:
            choice = read_int("Your choice: ")
            match choice:
                case 1:
                    handle_add_room(hotel)
                case 2:
                    list_available_rooms(hotel)
                case 3:
                    handle_create_booking(hotel)
                case 4:
                    handle_cancel_booking(hotel)
                case 5:
                    break
                case _:
                    print("Invalid menu point")
        except (ValueError, BookingError) as error:
            print(f"Error: {error}")
        except (KeyboardInterrupt, EOFError):
            print()
            break
    print("---GOOD BYE---")
