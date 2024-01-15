import streamlit as st

# Function to allocate work (from previous code)
def allocate_work(staff_licenses, state_workloads):
    staff_hours = {staff: 0 for staff in staff_licenses}  # Track hours allocated to each staff
    staff_allocations = {staff: {} for staff in staff_licenses}  # Track work allocation for each staff

    for state, hours_needed in state_workloads.items():
        while hours_needed > 0:
            # Find staff licensed in the state and with available hours
            available_staff = [s for s in staff_licenses if state in staff_licenses[s] and staff_hours[s] < 40]

            if not available_staff:
                print(f"Cannot allocate all work for {state}, {hours_needed} hours remain unallocated.")
                break  # No available staff for this state

            # Distribute workload evenly among available staff
            hours_per_staff = min(hours_needed // len(available_staff), 40)
            for staff in available_staff:
                allocated_hours = min(hours_per_staff, 40 - staff_hours[staff])
                staff_hours[staff] += allocated_hours
                staff_allocations[staff][state] = staff_allocations[staff].get(state, 0) + allocated_hours
                hours_needed -= allocated_hours

    return staff_allocations

import streamlit as st

# Streamlit interface
st.title("Work Allocation App")

# List of states for the dropdown
states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 
          'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 
          'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 
          'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 
          'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 
          'West Virginia', 'Wisconsin', 'Wyoming']

# Dynamic input for staff licenses
st.write("Enter Staff Licenses:")
staff_licenses = {}
staff_num = st.number_input('Number of staff members', min_value=1, max_value=20, value=5)
for i in range(staff_num):
    staff_name = st.text_input(f'Staff member {i+1} name', value=f'Staff {i+1}', key=f'staff_{i}_name')
    licenses = st.multiselect(f'Select states for {staff_name}', states, key=f'staff_{i}_licenses')
    staff_licenses[staff_name] = licenses

# Dynamic input for state workloads
st.write("Enter State Workloads:")
state_workloads = {}
state_num = st.number_input('Number of states to enter workloads for', min_value=1, max_value=len(states), value=3)
for i in range(state_num):
    state = st.selectbox(f'State {i+1}', states, key=f'state_{i}')
    hours = st.number_input(f'Hours needed for {state}', min_value=0, max_value=1000, value=40, key=f'hours_{i}')
    state_workloads[state] = hours

# Button to perform allocation
if st.button('Allocate Work'):
    allocations = allocate_work(staff_licenses, state_workloads)
    
    # Displaying the results in a table
    st.write("Allocation Results:")
    for staff, allocation in allocations.items():
        st.write(f"{staff}: {allocation}")

