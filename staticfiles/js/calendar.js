// Initialize FullCalendar on DOM load
document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            events: events, // Loaded from dashboard template
            eventClick: function(info) {
                alert(`Task: ${info.event.title}\nDue: ${info.event.start.toLocaleString()}`);
            },
            eventColor: '#3788d8',
            eventBackgroundColor: function(event) {
                return event.status === 'completed' ? '#28a745' : '#3788d8';
            }
        });
        calendar.render();
    }
});