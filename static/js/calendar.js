document.addEventListener('DOMContentLoaded', function() {
    console.log('Calendar script loaded');
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        console.log('Calendar element found');
        console.log('Events:', events);
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            events: events,
            eventClick: function(info) {
                // Populate modal with event details
                document.getElementById('eventTitle').textContent = info.event.title;
                document.getElementById('eventDueDate').textContent = info.event.start.toLocaleString();
                document.getElementById('eventStatus').textContent = info.event.extendedProps.status || 'Unknown';
                
                // Show the modal
                const modal = new bootstrap.Modal(document.getElementById('eventModal'));
                modal.show();
            },
            eventColor: '#3788d8',
            eventBackgroundColor: function(event) {
                return event.status === 'completed' ? '#28a745' : '#3788d8';
            }
        });
        calendar.render();
        console.log('Calendar rendered');
    } else {
        console.error('Calendar element not found');
    }
});