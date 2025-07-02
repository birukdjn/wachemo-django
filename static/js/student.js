
// document.addEventListener('DOMContentLoaded', function() {
//     // Calendar navigation
//     const prevBtn = document.getElementById('prevMonth');
//     const nextBtn = document.getElementById('nextMonth');
//     const monthYear = document.getElementById('current-month');
    
//     let currentDate = new Date();
    
//     function renderCalendar() {
//         const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
//         const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
//         const daysInMonth = lastDay.getDate();
//         const startingDay = firstDay.getDay();
        
//         monthYear.textContent = currentDate.toLocaleString('default', { month: 'long', year: 'numeric' });
        
//         let calendarBody = document.getElementById('calendar-body');
//         calendarBody.innerHTML = '';
        
//         let date = 1;
//         for (let i = 0; i < 6; i++) {
//             if (date > daysInMonth) break;
            
//             let row = document.createElement('tr');
            
//             for (let j = 0; j < 7; j++) {
//                 let cell = document.createElement('td');
//                 cell.className = 'text-center';
                
//                 if (i === 0 && j < startingDay) {
//                     cell.textContent = '';
//                 } else if (date > daysInMonth) {
//                     cell.textContent = '';
//                 } else {
//                     cell.textContent = date;
                    
//                     // Add event indicators (example)
//                     if (date === 15) {
//                         cell.innerHTML += '<div class="event-dot bg-primary"></div>';
//                         cell.classList.add('has-event');
//                     } else if (date === 22) {
//                         cell.innerHTML += '<div class="event-dot bg-success"></div>';
//                         cell.classList.add('has-event');
//                     } else if (date >= 26 && date <= 30) {
//                         cell.innerHTML += '<div class="event-dot bg-danger"></div>';
//                         cell.classList.add('has-event');
//                     }
                    
//                     // Highlight current day
//                     if (date === new Date().getDate() && 
//                         currentDate.getMonth() === new Date().getMonth() && 
//                         currentDate.getFullYear() === new Date().getFullYear()) {
//                         cell.classList.add('current-day');
//                     }
                    
//                     date++;
//                 }
                
//                 row.appendChild(cell);
//             }
            
//             calendarBody.appendChild(row);
//         }
//     }
    
//     prevBtn.addEventListener('click', function() {
//         currentDate.setMonth(currentDate.getMonth() - 1);
//         renderCalendar();
//     });
    
//     nextBtn.addEventListener('click', function() {
//         currentDate.setMonth(currentDate.getMonth() + 1);
//         renderCalendar();
//     });
    
//     // Initialize calendar
//     renderCalendar();
    
//     // Event click handlers
//     document.querySelectorAll('.has-event').forEach(cell => {
//         cell.addEventListener('click', function() {
//             // In a real app, you would fetch event details based on the date
//             $('#eventModal').modal('show');
//         });
//     });
    
//     // Upcoming event list items click handlers
//     document.querySelectorAll('.list-group-item').forEach(item => {
//         item.addEventListener('click', function() {
//             // In a real app, you would fetch event details based on the event
//             $('#eventModal').modal('show');
//         });
//     });
// });



// document.addEventListener('DOMContentLoaded', function() {
//     document.querySelectorAll('.year-selector').forEach(function(btn) {
//         btn.addEventListener('click', function() {
//             document.querySelectorAll('.year-selector').forEach(function(b) {
//                 b.classList.remove('btn-primary');
//                 b.classList.add('btn-outline-primary');
//             });
//             this.classList.remove('btn-outline-primary');
//             this.classList.add('btn-primary');
//             // Optionally, trigger a form submit or AJAX call here
//         });
//     });
//     // Prev/Next icons (static, no scroll logic for 5 years)
//     document.getElementById('prevYearBtn').addEventListener('click', function() {
//         // Optionally, add logic to scroll or change years
//     });
//     document.getElementById('nextYearBtn').addEventListener('click', function() {
//         // Optionally, add logic to scroll or change years
//     });
// });


// document.addEventListener('DOMContentLoaded', function() {
//     // Calendar navigation
//     const prevBtn = document.getElementById('prevMonth');
//     const nextBtn = document.getElementById('nextMonth');
//     const prevYearBtn = document.getElementById('prevYearBtn');
//     const nextYearBtn = document.getElementById('nextYearBtn');
//     const monthYear = document.getElementById('current-month');
//     const yearSelectors = document.querySelectorAll('.year-selector');
    
//     let currentDate = new Date();
//     let selectedYear = currentDate.getFullYear();
    
//     // Initialize with the current year selected
//     updateYearSelection(selectedYear);
    
//     function renderCalendar() {
//         const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
//         const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
//         const daysInMonth = lastDay.getDate();
//         const startingDay = firstDay.getDay();
        
//         monthYear.textContent = currentDate.toLocaleString('default', { month: 'long', year: 'numeric' });
        
//         let calendarBody = document.getElementById('calendar-body');
//         calendarBody.innerHTML = '';
        
//         let date = 1;
//         for (let i = 0; i < 6; i++) {
//             if (date > daysInMonth) break;
            
//             let row = document.createElement('tr');
            
//             for (let j = 0; j < 7; j++) {
//                 let cell = document.createElement('td');
//                 cell.className = 'text-center';
                
//                 if (i === 0 && j < startingDay) {
//                     cell.textContent = '';
//                 } else if (date > daysInMonth) {
//                     cell.textContent = '';
//                 } else {
//                     cell.textContent = date;
                    
//                     // Add event indicators (example)
//                     if (date === 15 && currentDate.getMonth() === 5) { // June 15
//                         cell.innerHTML += '<div class="event-dot bg-primary"></div>';
//                         cell.classList.add('has-event');
//                     } else if (date === 22 && currentDate.getMonth() === 5) { // June 22
//                         cell.innerHTML += '<div class="event-dot bg-success"></div>';
//                         cell.classList.add('has-event');
//                     } else if (date >= 26 && date <= 30 && currentDate.getMonth() === 5) { // June 26-30
//                         cell.innerHTML += '<div class="event-dot bg-danger"></div>';
//                         cell.classList.add('has-event');
//                     }
                    
//                     // Highlight current day
//                     if (date === new Date().getDate() && 
//                         currentDate.getMonth() === new Date().getMonth() && 
//                         currentDate.getFullYear() === new Date().getFullYear()) {
//                         cell.classList.add('current-day');
//                     }
                    
//                     date++;
//                 }
                
//                 row.appendChild(cell);
//             }
            
//             calendarBody.appendChild(row);
//         }
//     }
    
//     function updateYearSelection(year) {
//         // Update all year selector buttons
//         yearSelectors.forEach(btn => {
//             if (parseInt(btn.dataset.year) === year) {
//                 btn.classList.remove('btn-outline-primary');
//                 btn.classList.add('btn-primary');
//             } else {
//                 btn.classList.remove('btn-primary');
//                 btn.classList.add('btn-outline-primary');
//             }
//         });
        
//         // Update the selected year
//         selectedYear = year;
//     }
    
//     // Month navigation handlers
//     prevBtn.addEventListener('click', function() {
//         currentDate.setMonth(currentDate.getMonth() - 1);
//         renderCalendar();
//     });
    
//     nextBtn.addEventListener('click', function() {
//         currentDate.setMonth(currentDate.getMonth() + 1);
//         renderCalendar();
//     });
    
//     // Year navigation handlers
//     prevYearBtn.addEventListener('click', function() {
//         const newYear = selectedYear - 1;
//         currentDate.setFullYear(newYear);
//         updateYearSelection(newYear);
//         renderCalendar();
//     });
    
//     nextYearBtn.addEventListener('click', function() {
//         const newYear = selectedYear + 1;
//         currentDate.setFullYear(newYear);
//         updateYearSelection(newYear);
//         renderCalendar();
//     });
    
//     // Year selector click handlers
//     yearSelectors.forEach(btn => {
//         btn.addEventListener('click', function() {
//             const selectedYear = parseInt(this.dataset.year);
//             currentDate.setFullYear(selectedYear);
//             updateYearSelection(selectedYear);
//             renderCalendar();
//         });
//     });
    
//     // Event click handlers
//     document.querySelectorAll('.has-event').forEach(cell => {
//         cell.addEventListener('click', function() {
//             $('#eventModal').modal('show');
//         });
//     });
    
//     // Upcoming event list items click handlers
//     document.querySelectorAll('.list-group-item').forEach(item => {
//         item.addEventListener('click', function() {
//             $('#eventModal').modal('show');
//         });
//     });
    
//     // Initialize calendar
//     renderCalendar();
// });







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



  document.addEventListener("DOMContentLoaded", function () {
    function showSection(section) {
      document.querySelectorAll(".dashboard-section").forEach(function (div) {
        div.classList.add("d-none");
      });
      var target = document.getElementById("section-" + section);
      if (target) target.classList.remove("d-none");
      // Update active class on sidebar
      document
        .querySelectorAll("#sidebarMenu .nav-link")
        .forEach(function (link) {
          if (link.dataset.section === section) {
            link.classList.add("active");
          } else {
            link.classList.remove("active");
          }
        });
    }

    // Sidebar links
    document
      .querySelectorAll("#sidebarMenu .nav-link[data-section]")
      .forEach(function (link) {
        link.addEventListener("click", function (e) {
          e.preventDefault();
          showSection(this.dataset.section);
        });
      });

    // Dashboard cards
    document
      .querySelectorAll(".dashboard-section .btn[data-section]")
      .forEach(function (btn) {
        btn.addEventListener("click", function (e) {
          e.preventDefault();
          showSection(this.dataset.section);
        });
      });

    // Show dashboard by default
    showSection("dashboard");
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
