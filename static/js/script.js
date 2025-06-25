// Vehicle Parking App JavaScript

document.addEventListener("DOMContentLoaded", () => {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))
  
    // Auto-hide alerts after 5 seconds
    setTimeout(() => {
      var alerts = document.querySelectorAll(".alert")
      alerts.forEach((alert) => {
        var bsAlert = new bootstrap.Alert(alert)
        bsAlert.close()
      })
    }, 5000)
  
    // Form validation
    var forms = document.querySelectorAll(".needs-validation")
    Array.prototype.slice.call(forms).forEach((form) => {
      form.addEventListener(
        "submit",
        (event) => {
          if (!form.checkValidity()) {
            event.preventDefault()
            event.stopPropagation()
          }
          form.classList.add("was-validated")
        },
        false,
      )
    })
  
    // Real-time dashboard updates (if on dashboard page)
    if (window.location.pathname.includes("dashboard")) {
      setInterval(updateDashboardStats, 30000) // Update every 30 seconds
    }
  
    // Vehicle number formatting
    var vehicleInputs = document.querySelectorAll('input[name="vehicle_number"]')
    vehicleInputs.forEach((input) => {
      input.addEventListener("input", (e) => {
        // Convert to uppercase
        e.target.value = e.target.value.toUpperCase()
      })
    })
  
    // Confirm delete actions
    var deleteButtons = document.querySelectorAll('.btn-danger[data-action="delete"]')
    deleteButtons.forEach((button) => {
      button.addEventListener("click", (e) => {
        if (!confirm("Are you sure you want to delete this item? This action cannot be undone.")) {
          e.preventDefault()
        }
      })
    })
  
    // Loading states for forms
    var submitButtons = document.querySelectorAll('button[type="submit"]')
    submitButtons.forEach((button) => {
      button.addEventListener("click", () => {
        var form = button.closest("form")
        if (form && form.checkValidity()) {
          button.innerHTML = '<span class="loading"></span> Processing...'
          button.disabled = true
        }
      })
    })
  })
  
  // Function to update dashboard statistics
  function updateDashboardStats() {
    fetch("/api/dashboard-stats")
      .then((response) => response.json())
      .then((data) => {
        // Update stat cards if they exist
        updateStatCard("total-lots", data.total_lots)
        updateStatCard("total-spots", data.total_spots)
        updateStatCard("total-available", data.total_available)
        updateStatCard("total-occupied", data.total_occupied)
        updateStatCard("total-users", data.total_users)
        updateStatCard("active-reservations", data.active_reservations)
      })
      .catch((error) => {
        console.log("Dashboard update failed:", error)
      })
  }
  
  // Helper function to update stat cards
  function updateStatCard(elementId, value) {
    var element = document.getElementById(elementId)
    if (element) {
      element.textContent = value
    }
  }
  
  // Function to format currency
  function formatCurrency(amount) {
    return "₹" + Number.parseFloat(amount).toFixed(2)
  }
  
  // Function to format duration
  function formatDuration(hours) {
    if (hours < 1) {
      return Math.round(hours * 60) + " minutes"
    } else {
      return hours.toFixed(1) + " hours"
    }
  }
  
  // Function to show loading spinner
  function showLoading(element) {
    element.innerHTML = '<span class="loading"></span> Loading...'
    element.disabled = true
  }
  
  // Function to hide loading spinner
  function hideLoading(element, originalText) {
    element.innerHTML = originalText
    element.disabled = false
  }
  
  // Function to show toast notifications
  function showToast(message, type = "info") {
    var toastContainer = document.getElementById("toast-container")
    if (!toastContainer) {
      toastContainer = document.createElement("div")
      toastContainer.id = "toast-container"
      toastContainer.className = "position-fixed top-0 end-0 p-3"
      toastContainer.style.zIndex = "1055"
      document.body.appendChild(toastContainer)
    }
  
    var toastElement = document.createElement("div")
    toastElement.className = `toast align-items-center text-white bg-${type} border-0`
    toastElement.setAttribute("role", "alert")
    toastElement.innerHTML = `
          <div class="d-flex">
              <div class="toast-body">${message}</div>
              <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
          </div>
      `
  
    toastContainer.appendChild(toastElement)
    var toast = new bootstrap.Toast(toastElement)
    toast.show()
  
    // Remove toast element after it's hidden
    toastElement.addEventListener("hidden.bs.toast", () => {
      toastElement.remove()
    })
  }
  
  // API helper functions
  const API = {
    // Get parking lots
    getParkingLots: () => fetch("/api/parking-lots").then((response) => response.json()),
  
    // Get spots for a lot
    getLotSpots: (lotId) => fetch(`/api/parking-lots/${lotId}/spots`).then((response) => response.json()),
  
    // Create reservation
    createReservation: (lotId, vehicleNumber) =>
      fetch("/api/reservations", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          lot_id: lotId,
          vehicle_number: vehicleNumber,
        }),
      }).then((response) => response.json()),
  
    // Release reservation
    releaseReservation: (reservationId) =>
      fetch(`/api/reservations/${reservationId}/release`, {
        method: "POST",
      }).then((response) => response.json()),
  }
  
  // Export functions for use in other scripts
  window.ParkingApp = {
    updateDashboardStats,
    showToast,
    formatCurrency,
    formatDuration,
    API,
  }
  
  