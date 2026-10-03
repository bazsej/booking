# Hotel Manager

A console application for managing rooms and bookings in a hotel.

Requires Python 3.10+

## Features

- Create rooms in a hotel
- Create bookings in the available rooms
- Cancel bookings

## Structure

- **Data classes:** `Room`, `RoomType`, `Booking`
- **Business logic:** `Hotel`

## Validation

Validation is implemented in:

- Room creation
- Booking creation
- Booking cancellation

Test cases cover the main logic and validations.

## Usage

Run the program:

```bash
python booking.py
```

Run the tests:

```bash
python -m unittest booking
```
