import streamlit as st
import pandas as pd

def allocate_work(staff_licenses, state_workloads, hours, weeks):
    limit = hours * weeks  # Total hours available for work
    staff_hours = {staff: 0 for staff in staff_licenses}  # Track hours allocated to each staff
    staff_allocations = {staff: {} for staff in staff_licenses}  # Track work allocation for each staff
    unallocated_work = {}  # Track unallocated work

    for state, hours_needed in state_workloads.items():
        while hours_needed > 0:
            # Find staff licensed in the state and with available hours
            available_staff = [s for s in staff_licenses if state in staff_licenses[s] and staff_hours[s] < limit]

            if not available_staff:
                unallocated_work[state] = unallocated_work.get(state, 0) + hours_needed
                break

            # Distribute workload evenly among available staff
            hours_per_staff = min(hours_needed // len(available_staff), limit)
            for staff in available_staff:
                allocated_hours = min(hours_per_staff, limit - staff_hours[staff])
                staff_hours[staff] += allocated_hours
                staff_allocations[staff][state] = staff_allocations[staff].get(state, 0) + allocated_hours
                hours_needed -= allocated_hours

    return staff_allocations, unallocated_work


# Streamlit interface
st.title("Work Allocation App")

# List of states for the dropdown
states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 
          'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 
          'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 
          'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 
          'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 
          'West Virginia', 'Wisconsin', 'Wyoming']


# Input for number of work hours per week
work_hours_per_week = st.number_input('Enter number of work hours per week', min_value=1, max_value=168, value=40)

# Input for number of weeks
num_weeks = st.number_input('Enter number of weeks', min_value=1, max_value=52, value=3)


# Dynamic input for staff licenses
st.write("Enter Staff Licenses:")
staff_licenses = {}
staff_num = st.number_input('Number of staff members', min_value=1, max_value=20, value=5)
default_staff_licenses = [['Arizona', 'Texas'], ['Texas', 'Florida', 'New York'], ['New York', 'Texas'], ['Arizona', 'Texas'], ['Florida']]
for i in range(staff_num):
    col1, col2 = st.columns([2, 3])
    with col2:
        licenses = st.multiselect(f'Select states for Staff {i+1}', states, default=default_staff_licenses[i], key=f'staff_{i}_licenses')
    with col1:
        staff_name = st.text_input(f'Staff member {i+1} name', value=f'Staff {i+1}', key=f'staff_{i}_name')
    staff_licenses[staff_name] = licenses

# Dynamic input for state workloads
st.write("Enter State Workloads:")
state_workloads = {}
state_num = st.number_input('Number of states to enter workloads for', min_value=1, max_value=len(states), value=4)
default_state_workloads = [('Florida', 80), ('Arizona', 120), ('New York', 80), ('Texas', 320)]
for i in range(state_num):
    col1, col2 = st.columns([1, 1])
    with col2:
        hours = st.number_input(f'Hours for State {i+1}', min_value=0, max_value=1000, value=default_state_workloads[i][1], key=f'hours_{i}')
    with col1:
        state = st.selectbox(f'State {i+1}', states, index=states.index(default_state_workloads[i][0]), key=f'state_{i}')
    state_workloads[state] = hours

# Button to perform allocation
if st.button('Allocate Work'):
    allocations, unallocated_work = allocate_work(staff_licenses, state_workloads, work_hours_per_week, num_weeks)
    
    # Displaying the results in a table
    st.write("Allocation Results:")
    df = pd.DataFrame([(staff, state, hours) for staff, states in allocations.items() for state, hours in states.items()],
                      columns=['Staff', 'State', 'Allocated Hours'])
    st.table(df)

    # Display warning if there is unallocated work
    if unallocated_work:
        st.warning("Warning: Not all work could be allocated due to insufficient or unavailable staff. Unallocated work:")
        for state, hours in unallocated_work.items():
            st.write(f"{state}: {hours} hours")
