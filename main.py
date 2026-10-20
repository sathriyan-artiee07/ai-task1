
# constant declaration
SHOWS_FILE = "shows.txt"
BOOKINGS_FILE = "bookings.txt"
LOG_FILE = "sample_run.txt"
ROWS = "ABCDE"
SEATS_PER_ROW = 8
PRICES = {"A": 150, "B": 150, "C": 200, "D": 200, "E": 250}
REFUND_PERCENT = 80


# output/input 
def show(text=""):
    print(text)
    file = open(LOG_FILE, "a")
    file.write(str(text) + "\n")
    file.close()


def ask(prompt):
    answer = input(prompt)
    file = open(LOG_FILE, "a")
    file.write(prompt + answer + "\n")
    file.close()
    return answer


# input handlers
def get_text(prompt):
    # keep asking until the user types something without | or ,
    while True:
        text = ask(prompt).strip()
        if text == "":
            show("Input cannot be empty.")
        elif "|" in text or "," in text:
            show("The | and , characters are not allowed.")
        else:
            return text


def get_int(prompt, low, high):
    # keep asking until the user types a whole number between low and high
    while True:
        text = ask(prompt).strip()
        try:
            number = int(text)
        except ValueError:
            show("Please enter a whole number.")
            continue
        if number < low or number > high:
            show(f"Number must be between {low} and {high}.")
        else:
            return number


# file functions
def load_shows():
    # read shows.txt into a list of dictionaries
    shows = []
    try:
        file = open(SHOWS_FILE, "r")
        for line in file:
            parts = line.strip().split("|")
            if len(parts) == 4 and parts[0] != "ShowID":
                shows.append({"id": parts[0], "movie": parts[1],
                              "date": parts[2], "time": parts[3]})
        file.close()
    except FileNotFoundError:
        pass  # no file exists
    return shows


def load_bookings():
    # read bookings.txt into a list of dictionaries
    bookings = []
    try:
        file = open(BOOKINGS_FILE, "r")
        for line in file:
            parts = line.strip().split("|")
            if len(parts) == 5 and parts[0] != "BookingID":
                try:
                    bookings.append({"id": parts[0], "show": parts[1],
                                     "name": parts[2],
                                     "seats": parts[3].split(","),
                                     "amount": int(parts[4])})
                except ValueError:
                    pass  # skip the damaged line
        file.close()
    except FileNotFoundError:
        pass
    return bookings


def save_bookings(bookings):
    # write every booking back to bookings.txt
    file = open(BOOKINGS_FILE, "w")
    file.write("BookingID|ShowID|CustomerName|Seats|Amount\n")
    for b in bookings:
        file.write(f"{b['id']}|{b['show']}|{b['name']}|{','.join(b['seats'])}|{b['amount']}\n")
    file.close()


def find_show(shows, code):
    # return the show with this ID, or None if not found
    for s in shows:
        if s["id"] == code:
            return s
    return None


def get_taken(bookings, show_id):
    # list of seats already booked for this show
    taken = []
    for b in bookings:
        if b["show"] == show_id:
            for seat in b["seats"]:
                taken.append(seat)
    return taken


def seat_exists(seat):
    # valid seats are A1 to E8
    if len(seat) < 2 or seat[0] not in ROWS or not seat[1:].isdigit():
        return False
    return int(seat[1:]) >= 1 and int(seat[1:]) <= SEATS_PER_ROW


def count_gaps(taken):
    # count free seats that have a booked seat on both sides
    count = 0
    for row in ROWS:
        for col in range(2, SEATS_PER_ROW):
            seat = row + str(col)
            left = row + str(col - 1)
            right = row + str(col + 1)
            if seat not in taken and left in taken and right in taken:
                count = count + 1
    return count


def next_booking_id(bookings):
    # one more than the highest booking number, like BK0010
    highest = 0
    for b in bookings:
        number = int(b["id"][2:])
        if number > highest:
            highest = number
    return f"BK{highest + 1:04d}"


def show_list(shows):
    show("ID   Movie              Date        Time")
    for s in shows:
        show(f"{s['id']:<4} {s['movie']:<18} {s['date']:<11} {s['time']}")


def pick_show(shows):
    # show all shows and ask for one, returns None if not found
    show_list(shows)
    code = ask("Enter show ID: ").strip().upper()
    s = find_show(shows, code)
    if s is None:
        show("Show not found.")
    return s


def print_map(s, bookings):
    taken = get_taken(bookings, s["id"])
    show(f"\n{s['movie']} | {s['date']} {s['time']}")
    show("\n----- SCREEN -----")
    show("   1  2  3  4  5  6  7  8")
    for row in ROWS:
        line = row + " "
        for col in range(1, SEATS_PER_ROW + 1):
            if row + str(col) in taken:
                line = line + "[X]"
            else:
                line = line + "[ ]"
        show(f"{line}  Rs. {PRICES[row]}")


# menu features
def list_shows(shows, bookings):
    show_list(shows)


def seat_map(shows, bookings):
    s = pick_show(shows)
    if s is not None:
        print_map(s, bookings)


def book_seats(shows, bookings):
    s = pick_show(shows)
    if s is None:
        return
    print_map(s, bookings)
    taken = get_taken(bookings, s["id"])
    while True:
        text = ask("\nSeats to book, e.g. B3,B4 (Enter = go back): ")
        text = text.upper().replace(" ", "")
        if text == "":
            return
        seats = text.split(",")
        ok = True
        for seat in seats:
            if not seat_exists(seat):
                show(f"Seat {seat} does not exist. Choose other seats.")
                ok = False
            elif seat in taken:
                show(f"Seat {seat} is already booked. Choose other seats.")
                ok = False
            elif seats.count(seat) > 1:
                show(f"Seat {seat} is typed twice. Choose other seats.")
                ok = False
        if ok and count_gaps(taken + seats) > count_gaps(taken):
            show("This leaves a single empty seat between booked seats. Choose other seats.")
            ok = False
        if ok:
            break
    name = get_text("Customer name: ")
    total = 0
    for seat in seats:
        total = total + PRICES[seat[0]]
    booking_id = next_booking_id(bookings)
    bookings.append({"id": booking_id, "show": s["id"], "name": name,
                     "seats": seats, "amount": total})
    save_bookings(bookings)
    show("\n------ BOOKING CONFIRMED ------")
    show(f"Booking ID: {booking_id}")
    show(f"Name: {name}")
    show(f"Show: {s['movie']} {s['date']} {s['time']}")
    for seat in seats:
        show(f"Seat {seat}: Rs. {PRICES[seat[0]]}")
    show(f"Total: Rs. {total}")
    show("-------------------------------")


def cancel_booking(shows, bookings):
    code = ask("Booking ID to cancel: ").strip().upper()
    for b in bookings:
        if b["id"] == code:
            answer = ask(f"Cancel {code} ({','.join(b['seats'])}, Rs. {b['amount']})? (y/n): ").strip().lower()
            if answer == "y":
                refund = b["amount"] * REFUND_PERCENT / 100
                bookings.remove(b)
                save_bookings(bookings)
                show(f"Booking cancelled. Seats {','.join(b['seats'])} are free again.")
                show(f"Refund ({REFUND_PERCENT}%): Rs. {refund:.2f}")
            else:
                show("Cancelled.")
            return
    show("Booking not found.")


def report(shows, bookings):
    total_seats = len(ROWS) * SEATS_PER_ROW
    grand_total = 0
    for s in shows:
        count = len(get_taken(bookings, s["id"]))
        revenue = 0
        for b in bookings:
            if b["show"] == s["id"]:
                revenue = revenue + b["amount"]
        grand_total = grand_total + revenue
        percent = count * 100 / total_seats
        show(f"{s['id']} {s['movie']} {s['date']} {s['time']}: "
             f"{count}/{total_seats} seats, occupancy {percent:.1f}%, revenue Rs. {revenue}")
    show(f"TOTAL REVENUE: Rs. {grand_total}")


def best_seats(shows, bookings):
    # bonus: block of N adjacent free seats closest to the centre
    s = pick_show(shows)
    if s is None:
        return
    n = get_int("How many adjacent seats: ", 1, SEATS_PER_ROW)
    taken = get_taken(bookings, s["id"])
    best = None
    best_score = 0
    for r in range(len(ROWS)):
        for start in range(1, SEATS_PER_ROW - n + 2):
            block = []
            for col in range(start, start + n):
                block.append(ROWS[r] + str(col))
            free = True
            for seat in block:
                if seat in taken:
                    free = False
            if not free or count_gaps(taken + block) > count_gaps(taken):
                continue
            # distance of the block from the middle column and middle row
            score = abs(start + (n - 1) / 2 - 4.5) + abs(r - 2)
            if best is None or score < best_score:
                best = block
                best_score = score
    if best is None:
        show("No block of that size is available.")
    else:
        show(f"Best seats: {','.join(best)}")


# ---------- Menu ----------
def show_menu():
    show("\n===== MOVIE TICKET MENU =====")
    show("1. List shows           2. Seat map")
    show("3. Book seats           4. Cancel booking")
    show("5. Occupancy & revenue  6. Best seats")
    show("0. Exit")


def main():
    open(LOG_FILE, "w").close()    
    shows = load_shows()
    bookings = load_bookings()
    while True:
        show_menu()
        choice = get_int("Enter choice: ", 0, 6)
        if choice == 1:
            list_shows(shows, bookings)
        elif choice == 2:
            seat_map(shows, bookings)
        elif choice == 3:
            book_seats(shows, bookings)
        elif choice == 4:
            cancel_booking(shows, bookings)
        elif choice == 5:
            report(shows, bookings)
        elif choice == 6:
            best_seats(shows, bookings)
        else:
            show("Goodbye!")
            break


main()
