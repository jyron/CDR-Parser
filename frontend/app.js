// Global state
let allRecords = [];
let filteredRecords = [];
let currentSort = null; // 'asc', 'desc', or null

// API Configuration
const API_BASE_URL = "http://localhost:8000";

// DOM Elements
const loadingEl = document.getElementById("loading");
const errorEl = document.getElementById("error");
const errorMessageEl = document.getElementById("error-message");
const resultsEl = document.getElementById("results");
const recordCountEl = document.getElementById("record-count");
const recordsTbodyEl = document.getElementById("records-tbody");
const noResultsEl = document.getElementById("no-results");

// Filter inputs
const filterInputs = {
  id: document.getElementById("filter-id"),
  mnc: document.getElementById("filter-mnc"),
  bytes_used: document.getElementById("filter-bytes"),
  dmcc: document.getElementById("filter-dmcc"),
  cellid: document.getElementById("filter-cellid"),
  ip: document.getElementById("filter-ip"),
};

// Sort buttons
const sortBytesAscBtn = document.getElementById("sort-bytes-asc");
const sortBytesDescBtn = document.getElementById("sort-bytes-desc");

// Fetch records from API
async function fetchRecords() {
  try {
    showLoading();
    const response = await fetch(`${API_BASE_URL}/records`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    allRecords = await response.json();
    filteredRecords = [...allRecords];

    hideLoading();
    showResults();
    renderRecords();
    setupFilterListeners();
    setupSortListeners();
  } catch (error) {
    hideLoading();
    showError(error.message);
  }
}

// Filter records based on user input (OR logic)
function filterRecords() {
  const filters = {
    id: filterInputs.id.value.trim().toLowerCase(),
    mnc: filterInputs.mnc.value.trim().toLowerCase(),
    bytes_used: filterInputs.bytes_used.value.trim().toLowerCase(),
    dmcc: filterInputs.dmcc.value.trim().toLowerCase(),
    cellid: filterInputs.cellid.value.trim().toLowerCase(),
    ip: filterInputs.ip.value.trim().toLowerCase(),
  };

  // Check if any filter has a value
  const hasActiveFilters = Object.values(filters).some(
    (filter) => filter !== ""
  );

  if (!hasActiveFilters) {
    // No filters active, show all records
    filteredRecords = [...allRecords];
  } else {
    // OR logic: include record if it matches ANY filter
    filteredRecords = allRecords.filter((record) => {
      return Object.entries(filters).some(([field, filterValue]) => {
        if (filterValue === "") return false;

        const recordValue = record[field];

        // Handle null values
        if (recordValue === null || recordValue === undefined) {
          return false;
        }

        // Convert to string for comparison and make case-insensitive
        const recordValueStr = String(recordValue).toLowerCase();

        // Partial match
        return recordValueStr.includes(filterValue);
      });
    });
  }

  applySorting();
  renderRecords();
}

// Sort filtered records by bytes_used
function applySorting() {
  if (currentSort === "asc") {
    filteredRecords.sort((a, b) => {
      const aVal = a.bytes_used !== null ? a.bytes_used : -1;
      const bVal = b.bytes_used !== null ? b.bytes_used : -1;
      return aVal - bVal;
    });
  } else if (currentSort === "desc") {
    filteredRecords.sort((a, b) => {
      const aVal = a.bytes_used !== null ? a.bytes_used : -1;
      const bVal = b.bytes_used !== null ? b.bytes_used : -1;
      return bVal - aVal;
    });
  }
}

// Setup sort button listeners
function setupSortListeners() {
  sortBytesAscBtn.addEventListener("click", () => {
    if (currentSort === "asc") {
      // Toggle off
      currentSort = null;
      sortBytesAscBtn.classList.remove("active");
      sortBytesAscBtn.classList.add("btn-outline-light");
      sortBytesAscBtn.classList.remove("btn-light");
    } else {
      // Set ascending
      currentSort = "asc";
      sortBytesAscBtn.classList.add("active");
      sortBytesAscBtn.classList.remove("btn-outline-light");
      sortBytesAscBtn.classList.add("btn-light");
      sortBytesDescBtn.classList.remove("active");
      sortBytesDescBtn.classList.add("btn-outline-light");
      sortBytesDescBtn.classList.remove("btn-light");
    }
    applySorting();
    renderRecords();
  });

  sortBytesDescBtn.addEventListener("click", () => {
    if (currentSort === "desc") {
      // Toggle off
      currentSort = null;
      sortBytesDescBtn.classList.remove("active");
      sortBytesDescBtn.classList.add("btn-outline-light");
      sortBytesDescBtn.classList.remove("btn-light");
    } else {
      // Set descending
      currentSort = "desc";
      sortBytesDescBtn.classList.add("active");
      sortBytesDescBtn.classList.remove("btn-outline-light");
      sortBytesDescBtn.classList.add("btn-light");
      sortBytesAscBtn.classList.remove("active");
      sortBytesAscBtn.classList.add("btn-outline-light");
      sortBytesAscBtn.classList.remove("btn-light");
    }
    applySorting();
    renderRecords();
  });
}

// Render records to table
function renderRecords() {
  recordCountEl.textContent = filteredRecords.length;

  if (filteredRecords.length === 0) {
    recordsTbodyEl.innerHTML = "";
    noResultsEl.classList.remove("d-none");
  } else {
    noResultsEl.classList.add("d-none");

    recordsTbodyEl.innerHTML = filteredRecords
      .map(
        (record) => `
            <tr>
                <td>${record.id}</td>
                <td>${
                  record.mnc !== null
                    ? record.mnc
                    : '<em class="text-muted">null</em>'
                }</td>
                <td>${
                  record.bytes_used !== null
                    ? record.bytes_used
                    : '<em class="text-muted">null</em>'
                }</td>
                <td>${
                  record.dmcc !== null
                    ? record.dmcc
                    : '<em class="text-muted">null</em>'
                }</td>
                <td>${
                  record.cellid !== null
                    ? record.cellid
                    : '<em class="text-muted">null</em>'
                }</td>
                <td>${
                  record.ip !== null
                    ? record.ip
                    : '<em class="text-muted">null</em>'
                }</td>
            </tr>
        `
      )
      .join("");
  }
}

// Setup event listeners for filter inputs
function setupFilterListeners() {
  Object.values(filterInputs).forEach((input) => {
    input.addEventListener("input", filterRecords);
  });
}

// UI State Management
function showLoading() {
  loadingEl.classList.remove("d-none");
  errorEl.classList.add("d-none");
  resultsEl.classList.add("d-none");
}

function hideLoading() {
  loadingEl.classList.add("d-none");
}

function showError(message) {
  errorMessageEl.textContent = message;
  errorEl.classList.remove("d-none");
  resultsEl.classList.add("d-none");
}

function showResults() {
  errorEl.classList.add("d-none");
  resultsEl.classList.remove("d-none");
}

// Initialize app
document.addEventListener("DOMContentLoaded", fetchRecords);
