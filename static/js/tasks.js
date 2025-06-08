// Get CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie("csrftoken");

// Format date for display
function formatDate(dateStr) {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return date.toLocaleString("en-US", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Load tasks from API
function loadTasks() {
  fetch("/api/tasks/")
    .then((response) => {
      if (!response.ok) throw new Error("Failed to fetch tasks");
      return response.json();
    })
    .then((data) => {
      const tasks = data.results || data;
      const tbody = document.getElementById("taskTableBody");
      tbody.innerHTML = "";
      if (tasks.length === 0) {
        tbody.innerHTML =
          '<tr><td colspan="4" class="text-center text-muted">No tasks found.</td></tr>';
      } else {
        tasks.forEach((task) => {
          const row = document.createElement("tr");
          row.innerHTML = `
                        <td>${task.title}</td>
                        <td>${formatDate(task.due_date)}</td>
                        <td>
                            <span class="badge ${
                              task.status === "completed"
                                ? "bg-success"
                                : "bg-warning"
                            }">
                                ${
                                  task.status.charAt(0).toUpperCase() +
                                  task.status.slice(1)
                                }
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-outline-warning me-1" onclick="openTaskModal(${
                              task.id
                            })">Edit</button>
                            <button class="btn btn-sm btn-outline-danger" data-bs-toggle="modal" data-bs-target="#deleteModal" data-task-id="${
                              task.id
                            }" data-task-title="${task.title}">Delete</button>
                        </td>
                    `;
          tbody.appendChild(row);
        });
      }
      loadCalendar(tasks);
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Failed to load tasks.");
    });
}

// Load FullCalendar
function loadCalendar(tasks) {
  const events = tasks.map((task) => ({
    title: task.title,
    description: task.description || "",
    start: task.due_date || new Date().toISOString(),
    id: task.id,
    status: task.status,
  }));
  const calendarEl = document.getElementById("calendar");
  if (calendarEl) {
    const calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: "dayGridMonth",
      events: events,
      eventClick: function (info) {
        document.getElementById("eventTitle").textContent = info.event.title;
        document.getElementById("eventDescription").textContent =
          info.event.extendedProps.description || "No description";
        document.getElementById("eventDueDate").textContent = formatDate(
          info.event.start
        );
        document.getElementById("eventStatus").textContent =
          info.event.extendedProps.status || "Unknown";
        const modal = new bootstrap.Modal(
          document.getElementById("eventModal")
        );
        modal.show();
      },
      eventColor: "#3788d8",
      eventBackgroundColor: function (event) {
        return event.status === "completed" ? "#28a745" : "#3788d8";
      },
    });
    calendar.render();
  }
}

// Open task modal for create/edit
function openTaskModal(taskId = null) {
  const modal = new bootstrap.Modal(document.getElementById("taskModal"));
  const form = document.getElementById("taskForm");
  const title = document.getElementById("taskTitle");
  const description = document.getElementById("taskDescription");
  const dueDate = document.getElementById("taskDueDate");
  const status = document.getElementById("taskStatus");
  const taskIdInput = document.getElementById("taskId");
  const modalTitle = document.getElementById("taskModalLabel");

  if (taskId) {
    modalTitle.textContent = "Edit Task";
    fetch(`/api/tasks/${taskId}/`)
      .then((response) => {
        if (!response.ok) throw new Error("Failed to fetch task");
        return response.json();
      })
      .then((task) => {
        taskIdInput.value = task.id;
        title.value = task.title;
        description.value = task.description || "";
        dueDate.value = task.due_date
          ? new Date(task.due_date).toISOString().slice(0, 16)
          : "";
        status.value = task.status;
        modal.show();
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("Failed to load task.");
      });
  } else {
    modalTitle.textContent = "Create Task";
    taskIdInput.value = "";
    form.reset();
    modal.show();
  }
}

// Handle task form submission
document.addEventListener("DOMContentLoaded", function () {
  loadTasks();

  const taskForm = document.getElementById("taskForm");
  taskForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const taskId = document.getElementById("taskId").value;
    const taskData = {
      title: document.getElementById("taskTitle").value,
      description: document.getElementById("taskDescription").value,
      due_date: document.getElementById("taskDueDate").value,
      status: document.getElementById("taskStatus").value,
    };

    const method = taskId ? "PUT" : "POST";
    const url = taskId ? `/api/tasks/${taskId}/` : "/api/tasks/";
    fetch(url, {
      method: method,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify(taskData),
    })
      .then((response) => {
        if (!response.ok) throw new Error("Failed to save task");
        return response.json();
      })
      .then(() => {
        // Close modal and clean up
        const modal = bootstrap.Modal.getInstance(
          document.getElementById("taskModal")
        );
        if (modal) modal.hide();
        // Forcefully remove backdrop and modal-open class
        document.body.classList.remove("modal-open");
        document.body.style.overflow = "";
        document.body.style.paddingRight = "";
        const backdrops = document.querySelectorAll(".modal-backdrop");
        backdrops.forEach((backdrop) => backdrop.remove());
        loadTasks();
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("Failed to save task.");
        // Close modal and clean up
        const modal = bootstrap.Modal.getInstance(
          document.getElementById("taskModal")
        );
        if (modal) modal.hide();
        // Forcefully remove backdrop and modal-open class
        document.body.classList.remove("modal-open");
        document.body.style.overflow = "";
        document.body.style.paddingRight = "";
        const backdrops = document.querySelectorAll(".modal-backdrop");
        backdrops.forEach((backdrop) => backdrop.remove());
      });
  });
  // Handle delete modal
  document.addEventListener("click", function (e) {
    if (e.target.matches('[data-bs-target="#deleteModal"]')) {
      const taskId = e.target.getAttribute("data-task-id");
      const taskTitle = e.target.getAttribute("data-task-title");
      document.getElementById("deleteTaskTitle").textContent = taskTitle;
      document.getElementById("confirmDelete").onclick = function () {
        fetch(`/api/tasks/${taskId}/`, {
          method: "DELETE",
          headers: {
            "X-CSRFToken": csrftoken,
          },
        })
          .then((response) => {
            if (!response.ok) throw new Error("Failed to delete task");
            bootstrap.Modal.getInstance(
              document.getElementById("deleteModal")
            ).hide();
            loadTasks();
          })
          .catch((error) => {
            console.error("Error:", error);
            alert("Failed to delete task.");
          });
      };
    }
  });
});
