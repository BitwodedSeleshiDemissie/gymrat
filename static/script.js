$(document).ready(function() {
    loadCalendar();
});

function loadCalendar() {
    const calendar = $('#calendar');
    calendar.html('');
    
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    days.forEach((day, index) => {
        const dayElement = $('<div>').addClass('calendar-day');
        dayElement.append($('<h4>').text(day));
        dayElement.append(createTimeSlots(index));
        dayElement.append($('<div>').addClass('bookings-list'));
        calendar.append(dayElement);
    });
    
    $.get('/get-bookings', function(bookings) {
        updateBookings(bookings);
    });
}

function createTimeSlots(index) {
    const slots = $('<div>');
    let currentTime = 23 * 60; // Start at 23:00 in minutes
    
    while (currentTime >= 6 * 60 + 15) { // Ensure the last slot ends by 21:15
        const slotEndTime = currentTime;
        const slotStartTime = currentTime - 105; // Subtract 1 hour and 45 minutes
        
        const startHours = Math.floor(slotStartTime / 60);
        const startMinutes = slotStartTime % 60;
        const endHours = Math.floor(slotEndTime / 60);
        const endMinutes = slotEndTime % 60;
        
        const startTime = `${startHours}:${startMinutes.toString().padStart(2, '0')}`;
        const endTime = `${endHours}:${endMinutes.toString().padStart(2, '0')}`;
        
        const slot = $('<div>').addClass('booking-slot').text(`${startTime} - ${endTime}`);
        slot.click(function() {
            selectSlot(slot);
        });
        slots.append(slot);
        
        currentTime -= 105; // Subtract 1 hour and 45 minutes
    }
    
    return slots;
}

function selectSlot(slot) {
    const time = slot.text();
    const day = slot.closest('.calendar-day').find('h4').text();
    $('#selected-slot').text(`${day} - ${time}`);
    $('#bookingModal').modal('show');
}
function deleteBooking(booking) {
    if (confirm('Are you sure you want to delete this booking?')) {
        $.ajax({
            url: '/delete-booking',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            data: JSON.stringify({
                username: booking.username,
                day: booking.day,
                time: booking.time
            }),
            success: function(response) {
                if (response.message === 'Booking deleted successfully') {
                    location.reload();
                }
            },
            error: function(xhr) {
                try {
                    const errorMessage = JSON.parse(xhr.responseText).error;
                    alert(errorMessage);
                } catch (e) {
                    alert('An error occurred while deleting the booking.');
                }
            }
        });
    }
}

function updateBookings(bookings) {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    
    // Clear existing bookings
    $('.bookings-list').empty();
    
    // Display bookings for each day
    days.forEach(day => {
        const dayBookings = bookings.filter(booking => booking.day_name === day);
        const dayElement = $(`.calendar-day:has(h4:contains('${day}'))`);
        const bookingsList = dayElement.find('.bookings-list');
        
        if (dayBookings.length > 0) {
            dayBookings.forEach(booking => {
                const bookingEntry = $('<div>').addClass('booking-entry');
                const bookingContent = `
                    <div class="booking-header">
                        <span class="booking-username">${booking.username}</span>
                        <span class="booking-time">${booking.time}</span>
                    </div>
                    <div class="booking-note">${booking.note}</div>
                    <button class="delete-button">Delete</button>
                `;
                bookingEntry.html(bookingContent);
                
                // Add delete button functionality
                bookingEntry.find('.delete-button').click(function() {
                    deleteBooking(booking);
                });
                
                bookingsList.append(bookingEntry);
            });
        } else {
            const noBookings = $('<div>').text('No bookings');
            bookingsList.append(noBookings);
        }
    });
}

function bookSlot() {
    const selectedSlot = $('#selected-slot');
    if (!selectedSlot.length) return;

    const dayName = selectedSlot.text().split(' - ')[0];
    const [startTime, endTime] = selectedSlot.text().split(' - ').slice(1);
    const note = $('#note').val();

    // Get the day index from the day name
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const day = days.indexOf(dayName);

    if (day === -1) {
        alert('Invalid day selected');
        return;
    }

    $.ajax({
        url: '/book-slot',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        data: JSON.stringify({
            day: day,
            time: `${startTime} - ${endTime}`,
            note: note
        }),
        success: function(response) {
            if (response.message) {
                updateBookings([response.booking]);
            }
        },
        error: function(xhr) {
            try {
                const errorMessage = JSON.parse(xhr.responseText).error;
                alert(errorMessage);
            } catch (e) {
                alert('An error occurred while booking the slot.');
            }
        }
    });
}

function logout() {
    $.ajax({
        url: '/logout',
        method: 'POST',
        success: function() {
            window.location.href = '/';
        }
    });
}