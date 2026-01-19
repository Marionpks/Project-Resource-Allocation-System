const API_URL = 'http://localhost:8000';

function openTab(tabName, event) {
    const tabs = document.querySelectorAll('.tab-content');
    const buttons = document.querySelectorAll('.tab-button');

    tabs.forEach(tab => tab.classList.remove('active'));
    buttons.forEach(btn => btn.classList.remove('active'));

    document.getElementById(tabName).classList.add('active');
    
    if (event && event.target) {
        event.target.classList.add('active');
    } else {
        buttons.forEach(btn => {
            if (btn.getAttribute('onclick').includes(tabName)) {
                btn.classList.add('active');
            }
        });
    }

    if (tabName === 'employees') loadEmployees();
    if (tabName === 'projects') loadProjects();
    if (tabName === 'allocations') {
        loadAllocations();
        loadEmployeesForDropdown();
        loadProjectsForDropdown();
    }
}

function showMessage(elementId, message, type) {
    const msgElement = document.getElementById(elementId);
    msgElement.textContent = message;
    msgElement.className = `message ${type} show`;
    setTimeout(() => msgElement.classList.remove('show'), 5000);
}

async function loadEmployees() {
    const listElement = document.getElementById('employees-list');
    listElement.innerHTML = '<div class="loading">Loading...</div>';

    try {
        const response = await fetch(`${API_URL}/read_employees`);
        const employees = await response.json();

        if (employees.length === 0) {
            listElement.innerHTML = '<div class="empty-state">No employees found. Add one above!</div>';
            return;
        }

        let html = '<table class="data-table"><thead><tr><th>ID</th><th>Name</th><th>Skills</th><th>Available Hours</th><th>Actions</th></tr></thead><tbody>';
        employees.forEach(emp => {
            html += `<tr>
                <td>${emp.employee_id}</td>
                <td>${emp.employee_name}</td>
                <td>${emp.skilled_language}</td>
                <td>${emp.available_hrs}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-small btn-edit" onclick="editEmployee(${emp.employee_id}, '${emp.employee_name.replace(/'/g, "\\'")}', '${emp.skilled_language.replace(/'/g, "\\'")}', ${emp.available_hrs})">Edit</button>
                        <button class="btn btn-small btn-delete" onclick="deleteEmployee(${emp.employee_id}, '${emp.employee_name.replace(/'/g, "\\'")}')">Delete</button>
                    </div>
                </td>
            </tr>`;
        });
        html += '</tbody></table>';
        listElement.innerHTML = html;
    } catch (error) {
        listElement.innerHTML = '<div class="empty-state">Failed to load employees</div>';
    }
}

async function loadProjects() {
    const listElement = document.getElementById('projects-list');
    listElement.innerHTML = '<div class="loading">Loading...</div>';

    try {
        const response = await fetch(`${API_URL}/read_projects`);
        const projects = await response.json();

        if (projects.length === 0) {
            listElement.innerHTML = '<div class="empty-state">No projects found. Add one above!</div>';
            return;
        }

        let html = '<table class="data-table"><thead><tr><th>ID</th><th>Project Name</th><th>Duration (hrs)</th><th>Skills Required</th><th>Actions</th></tr></thead><tbody>';
        projects.forEach(proj => {
            html += `<tr>
                <td>${proj.project_id}</td>
                <td>${proj.project_name}</td>
                <td>${proj.project_duration}</td>
                <td>${proj.project_skill_required}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-small btn-edit" onclick="editProject(${proj.project_id}, '${proj.project_name.replace(/'/g, "\\'")}', ${proj.project_duration}, '${proj.project_skill_required.replace(/'/g, "\\'")}')">Edit</button>
                        <button class="btn btn-small btn-delete" onclick="deleteProject(${proj.project_id}, '${proj.project_name.replace(/'/g, "\\'")}')">Delete</button>
                    </div>
                </td>
            </tr>`;
        });
        html += '</tbody></table>';
        listElement.innerHTML = html;
    } catch (error) {
        listElement.innerHTML = '<div class="empty-state">Failed to load projects</div>';
    }
}

async function loadEmployeesForDropdown() {
    try {
        const response = await fetch(`${API_URL}/read_employees`);
        const employees = await response.json();
        const select = document.getElementById('allocation_employee_id');
        select.innerHTML = '<option value="">Select Employee</option>';
        employees.forEach(emp => {
            select.innerHTML += `<option value="${emp.employee_id}">${emp.employee_name} (${emp.skilled_language})</option>`;
        });
    } catch (error) {
        console.error('Failed to load employees for dropdown');
    }
}

async function loadProjectsForDropdown() {
    try {
        const response = await fetch(`${API_URL}/read_projects`);
        const projects = await response.json();
        const select = document.getElementById('allocation_project_id');
        select.innerHTML = '<option value="">Select Project</option>';
        projects.forEach(proj => {
            select.innerHTML += `<option value="${proj.project_id}">${proj.project_name}</option>`;
        });
    } catch (error) {
        console.error('Failed to load projects for dropdown');
    }
}

async function loadAllocations() {
    const listElement = document.getElementById('allocations-list');
    listElement.innerHTML = '<div class="loading">Loading...</div>';

    try {
        const response = await fetch(`${API_URL}/read_allocations_detailed`);
        const allocations = await response.json();

        if (allocations.length === 0) {
            listElement.innerHTML = '<div class="empty-state">No allocations found. Create one above!</div>';
            return;
        }

        let html = '<table class="data-table"><thead><tr>';
        html += '<th>ID</th>';
        html += '<th>Employee</th>';
        html += '<th>Employee Skills</th>';
        html += '<th>Project</th>';
        html += '<th>Skills Required</th>';
        html += '<th>Hours Allocated</th>';
        html += '<th>Total Hours</th>';
        html += '<th>Remaining Hours</th>';
        html += '<th>Actions</th>';
        html += '</tr></thead><tbody>';
        
        allocations.forEach(alloc => {
            const skillsMatch = alloc.employee_skills.toLowerCase().includes(alloc.project_skills_required.toLowerCase()) ||
                              alloc.project_skills_required.toLowerCase().includes(alloc.employee_skills.toLowerCase());
            const skillsStyle = skillsMatch ? 'style="background-color: #e8e8e8;"' : '';
            
            html += `<tr ${skillsStyle}>
                <td>${alloc.allocation_id}</td>
                <td><strong>${alloc.employee_name}</strong></td>
                <td>${alloc.employee_skills}</td>
                <td><strong>${alloc.project_name}</strong></td>
                <td>${alloc.project_skills_required}</td>
                <td>${alloc.allocation_hours}</td>
                <td>${alloc.total_employee_hours}</td>
                <td>${alloc.remaining_hours}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-small btn-edit" onclick="editAllocation(${alloc.allocation_id}, ${alloc.employee_id}, ${alloc.project_id}, ${alloc.allocation_hours})">Edit</button>
                        <button class="btn btn-small btn-delete" onclick="deleteAllocation(${alloc.allocation_id})">Delete</button>
                    </div>
                </td>
            </tr>`;
        });
        html += '</tbody></table>';
        listElement.innerHTML = html;
    } catch (error) {
        listElement.innerHTML = '<div class="empty-state">Failed to load allocations</div>';
    }
}

loadEmployees();

let editingEmployeeId = null;
function editEmployee(id, name, skills, hours) {
    editingEmployeeId = id;
    document.getElementById('employee_name').value = name;
    document.getElementById('skilled_language').value = skills;
    document.getElementById('available_hrs').value = hours;
    document.querySelector('#employee-form button[type="submit"]').textContent = 'Update Employee';
    window.scrollTo(0, 0);
}

document.getElementById('employee-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = {
        employee_name: document.getElementById('employee_name').value,
        skilled_language: document.getElementById('skilled_language').value,
        available_hrs: parseInt(document.getElementById('available_hrs').value)
    };

    try {
        let response;
        if (editingEmployeeId) {
            response = await fetch(`${API_URL}/update_employee/${editingEmployeeId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
        } else {
            response = await fetch(`${API_URL}/create_employee`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
        }

        if (response.ok) {
            showMessage('employee-message', editingEmployeeId ? 'Employee updated successfully!' : 'Employee added successfully!', 'success');
            e.target.reset();
            editingEmployeeId = null;
            document.querySelector('#employee-form button[type="submit"]').textContent = 'Add Employee';
            loadEmployees();
        } else {
            const error = await response.json();
            showMessage('employee-message', `Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showMessage('employee-message', 'Failed to connect to server', 'error');
    }
});

async function deleteEmployee(id, name) {
    if (!confirm(`Are you sure you want to delete employee "${name}"?`)) return;

    try {
        const response = await fetch(`${API_URL}/delete_employee/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showMessage('employee-message', 'Employee deleted successfully!', 'success');
            loadEmployees();
        } else {
            const error = await response.json();
            showMessage('employee-message', `Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showMessage('employee-message', 'Failed to delete employee', 'error');
    }
}

let editingProjectId = null;
function editProject(id, name, duration, skills) {
    editingProjectId = id;
    document.getElementById('project_name').value = name;
    document.getElementById('project_duration').value = duration;
    document.getElementById('project_skill_required').value = skills;
    document.querySelector('#project-form button[type="submit"]').textContent = 'Update Project';
    window.scrollTo(0, 0);
}

document.getElementById('project-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = {
        project_name: document.getElementById('project_name').value,
        project_duration: parseInt(document.getElementById('project_duration').value),
        project_skill_required: document.getElementById('project_skill_required').value
    };

    try {
        let response;
        if (editingProjectId) {
            response = await fetch(`${API_URL}/update_project/${editingProjectId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
        } else {
            response = await fetch(`${API_URL}/create_project`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
        }

        if (response.ok) {
            showMessage('project-message', editingProjectId ? 'Project updated successfully!' : 'Project added successfully!', 'success');
            e.target.reset();
            editingProjectId = null;
            document.querySelector('#project-form button[type="submit"]').textContent = 'Add Project';
            loadProjects();
        } else {
            const error = await response.json();
            showMessage('project-message', `Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showMessage('project-message', 'Failed to connect to server', 'error');
    }
});

async function deleteProject(id, name) {
    if (!confirm(`Are you sure you want to delete project "${name}"?`)) return;

    try {
        const response = await fetch(`${API_URL}/delete_project/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showMessage('project-message', 'Project deleted successfully!', 'success');
            loadProjects();
        } else {
            const error = await response.json();
            showMessage('project-message', `Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showMessage('project-message', 'Failed to delete project', 'error');
    }
}

let editingAllocationId = null;
function editAllocation(id, employeeId, projectId, hours) {
    editingAllocationId = id;
    document.getElementById('allocation_employee_id').value = employeeId;
    document.getElementById('allocation_project_id').value = projectId;
    document.getElementById('allocation_hours').value = hours;
    document.querySelector('#allocation-form button[type="submit"]').textContent = 'Update Allocation';
    window.scrollTo(0, 0);
}

document.getElementById('allocation-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = {
        employee_id: parseInt(document.getElementById('allocation_employee_id').value),
        project_id: parseInt(document.getElementById('allocation_project_id').value),
        allocation_hours: parseInt(document.getElementById('allocation_hours').value)
    };

    try {
        let response;
        if (editingAllocationId) {
            response = await fetch(`${API_URL}/update_allocation/${editingAllocationId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
        } else {
            response = await fetch(`${API_URL}/create_allocation`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
        }

        if (response.ok) {
            showMessage('allocation-message', editingAllocationId ? 'Allocation updated successfully!' : 'Allocation created successfully!', 'success');
            e.target.reset();
            editingAllocationId = null;
            document.querySelector('#allocation-form button[type="submit"]').textContent = 'Create Allocation';
            loadAllocations();
        } else {
            const error = await response.json();
            showMessage('allocation-message', `Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showMessage('allocation-message', 'Failed to connect to server', 'error');
    }
});

async function deleteAllocation(id) {
    if (!confirm('Are you sure you want to delete this allocation?')) return;

    try {
        const response = await fetch(`${API_URL}/delete_allocation/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showMessage('allocation-message', 'Allocation deleted successfully!', 'success');
            loadAllocations();
        } else {
            const error = await response.json();
            showMessage('allocation-message', `Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showMessage('allocation-message', 'Failed to delete allocation', 'error');
    }
}
