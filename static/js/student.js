
document.addEventListener('DOMContentLoaded', function() {
    // Calendar elements
    const prevMonthBtn = document.getElementById('prevMonthBtn');
    const nextMonthBtn = document.getElementById('nextMonthBtn');
    const monthYear = document.getElementById('current-month');
    const monthSelectors = document.querySelectorAll('.month-selector');
    const monthContainer = document.querySelector('.month-selector-container');
    
    // Initialize with current date
    let currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    
    // Sample events data
    const events = {
        '2025-06-15': { title: 'Science Fair', type: 'academic', color: 'primary' },
        '2025-06-22': { title: 'Sports Day', type: 'sports', color: 'success' },
        '2025-06-26': { title: 'Mid-Term Exams', type: 'exam', color: 'danger' },
        '2025-07-05': { title: 'Parent-Teacher Meeting', type: 'meeting', color: 'warning' }
    };
    
    // Initialize calendar
    renderCalendar();
    centerCurrentMonth();
    
    function renderCalendar() {
        const year = currentYear;
        const month = currentDate.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDay = firstDay.getDay();
        
        // Update month/year display
        monthYear.textContent = currentDate.toLocaleString('default', { month: 'long', year: 'numeric' });
        
        // Update month selector buttons
        monthSelectors.forEach(btn => {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-outline-primary');
            if (parseInt(btn.dataset.month) === month) {
                btn.classList.remove('btn-outline-primary');
                btn.classList.add('btn-primary');
            }
        });
        
        // Clear and rebuild calendar
        let calendarBody = document.getElementById('calendar-body');
        calendarBody.innerHTML = '';
        
        let date = 1;
        for (let i = 0; i < 6; i++) {
            if (date > daysInMonth) break;
            
            let row = document.createElement('tr');
            
            for (let j = 0; j < 7; j++) {
                let cell = document.createElement('td');
                cell.className = 'text-center';
                
                if (i === 0 && j < startingDay) {
                    cell.textContent = '';
                } else if (date > daysInMonth) {
                    cell.textContent = '';
                } else {
                    cell.textContent = date;
                    
                    // Format date for event checking
                    const currentDateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(date).padStart(2, '0')}`;
                    
                    // Check for events
                    if (events[currentDateStr]) {
                        const event = events[currentDateStr];
                        cell.innerHTML += `<div class="event-dot bg-${event.color}"></div>`;
                        cell.classList.add('has-event');
                        cell.dataset.eventDate = currentDateStr;
                    }
                    
                    // Highlight current day
                    const today = new Date();
                    if (date === today.getDate() && 
                        month === today.getMonth() && 
                        year === today.getFullYear()) {
                        cell.classList.add('current-day');
                    }
                    
                    date++;
                }
                
                row.appendChild(cell);
            }
            
            calendarBody.appendChild(row);
        }
        
        // Reattach event handlers
        attachEventHandlers();
    }
    
    function centerCurrentMonth() {
        const currentMonthIndex = currentDate.getMonth();
        const monthSelectorWidth = 80; // Approximate width of each month button
        const scrollPosition = (currentMonthIndex - 3) * monthSelectorWidth;
        monthContainer.style.transform = `translateX(-${scrollPosition}px)`;
    }
    
    function attachEventHandlers() {
        // Calendar day click handlers
        document.querySelectorAll('.has-event').forEach(cell => {
            cell.addEventListener('click', function() {
                const eventDate = this.dataset.eventDate;
                const event = events[eventDate];
                
                // Update modal with event details
                document.getElementById('eventTitle').textContent = event.title;
                document.getElementById('eventDate').textContent = 
                    new Date(eventDate).toLocaleDateString('en-US', { 
                        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' 
                    });
                document.getElementById('eventCategory').textContent = event.type;
                document.getElementById('eventCategory').className = `badge bg-${event.color}`;
                
                $('#eventModal').modal('show');
            });
        });
    }
    
    // Month navigation handlers
    prevMonthBtn.addEventListener('click', function() {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
        centerCurrentMonth();
    });
    
    nextMonthBtn.addEventListener('click', function() {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
        centerCurrentMonth();
    });
    
    // Month selector click handlers
    monthSelectors.forEach(btn => {
        btn.addEventListener('click', function() {
            currentDate.setMonth(parseInt(this.dataset.month));
            renderCalendar();
            centerCurrentMonth();
        });
    });
});


document.addEventListener('DOMContentLoaded', function() {
    // Attendance calendar navigation
    const prevMonthAtt = document.getElementById('prevMonthAtt');
    const nextMonthAtt = document.getElementById('nextMonthAtt');
    let currentAttDate = new Date();
    
    function renderAttendanceCalendar() {
        const year = currentAttDate.getFullYear();
        const month = currentAttDate.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDay = firstDay.getDay();
        
        let calendarBody = document.getElementById('attendance-calendar-body');
        calendarBody.innerHTML = '';
        
        let date = 1;
        for (let i = 0; i < 6; i++) {
            if (date > daysInMonth) break;
            
            let row = document.createElement('tr');
            
            for (let j = 0; j < 7; j++) {
                let cell = document.createElement('td');
                cell.className = 'text-center';
                
                if (i === 0 && j < startingDay) {
                    cell.textContent = '';
                } else if (date > daysInMonth) {
                    cell.textContent = '';
                } else {
                    cell.textContent = date;
                    
                    // Sample attendance data - replace with real data
                    const dayOfWeek = new Date(year, month, date).getDay();
                    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
                    const isHoliday = date === 15 && month === 5; // Example holiday on June 15
                    
                    if (isWeekend) {
                        cell.classList.add('weekend');
                    } else if (isHoliday) {
                        cell.classList.add('holiday');
                    } else {
                        // Sample status - replace with real data
                        const status = ['present', 'absent', 'late', 'excused'][Math.floor(Math.random() * 4)];
                        cell.classList.add(status);
                    }
                    
                    // Highlight today
                    const today = new Date();
                    if (date === today.getDate() && 
                        month === today.getMonth() && 
                        year === today.getFullYear()) {
                        cell.classList.add('today');
                    }
                    
                    date++;
                }
                
                row.appendChild(cell);
            }
            
            calendarBody.appendChild(row);
        }
    }
    
    prevMonthAtt.addEventListener('click', function() {
        currentAttDate.setMonth(currentAttDate.getMonth() - 1);
        renderAttendanceCalendar();
    });
    
    nextMonthAtt.addEventListener('click', function() {
        currentAttDate.setMonth(currentAttDate.getMonth() + 1);
        renderAttendanceCalendar();
    });
    
    // Initialize attendance calendar
    renderAttendanceCalendar();
    
    // Filter application
    document.getElementById('applyFilters').addEventListener('click', function() {
        // In a real app, this would filter the attendance records
        alert('Filters would be applied here in a real implementation');
    });
});


// Attendance script
document.addEventListener('DOMContentLoaded', function() {
    // Attendance calendar navigation
    const prevMonthAtt = document.getElementById('prevMonthAtt');
    const nextMonthAtt = document.getElementById('nextMonthAtt');
    let currentAttDate = new Date();
    
    function renderAttendanceCalendar() {
        const year = currentAttDate.getFullYear();
        const month = currentAttDate.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDay = firstDay.getDay();
        
        let calendarBody = document.getElementById('attendance-calendar-body');
        calendarBody.innerHTML = '';
        
        let date = 1;
        for (let i = 0; i < 6; i++) {
            if (date > daysInMonth) break;
            
            let row = document.createElement('tr');
            
            for (let j = 0; j < 7; j++) {
                let cell = document.createElement('td');
                cell.className = 'text-center';
                
                if (i === 0 && j < startingDay) {
                    cell.textContent = '';
                } else if (date > daysInMonth) {
                    cell.textContent = '';
                } else {
                    cell.textContent = date;
                    
                    // Sample attendance data - replace with real data
                    const dayOfWeek = new Date(year, month, date).getDay();
                    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
                    const isHoliday = date === 15 && month === 5; // Example holiday on June 15
                    
                    if (isWeekend) {
                        cell.classList.add('weekend');
                    } else if (isHoliday) {
                        cell.classList.add('holiday');
                    } else {
                        // Sample status - replace with real data
                        const status = ['present', 'absent', 'late', 'excused'][Math.floor(Math.random() * 4)];
                        cell.classList.add(status);
                    }
                    
                    // Highlight today
                    const today = new Date();
                    if (date === today.getDate() && 
                        month === today.getMonth() && 
                        year === today.getFullYear()) {
                        cell.classList.add('today');
                    }
                    
                    date++;
                }
                
                row.appendChild(cell);
            }
            
            calendarBody.appendChild(row);
        }
    }
    
    prevMonthAtt.addEventListener('click', function() {
        currentAttDate.setMonth(currentAttDate.getMonth() - 1);
        renderAttendanceCalendar();
    });
    
    nextMonthAtt.addEventListener('click', function() {
        currentAttDate.setMonth(currentAttDate.getMonth() + 1);
        renderAttendanceCalendar();
    });
    
    // Initialize attendance calendar
    renderAttendanceCalendar();
    
    // Filter application
    document.getElementById('applyFilters').addEventListener('click', function() {
        // In a real app, this would filter the attendance records
        alert('Filters would be applied here in a real implementation');
    });
});
