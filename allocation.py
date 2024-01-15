import streamlit as st
import pandas as pd

def allocate_work(staff_licenses, state_workloads):
    staff_hours = {staff: 0 for staff in staff_licenses}  # Track hours allocated to each staff
    staff_allocations = {staff: {} for staff in staff_licenses}  # Track work allocation for each staff
    unallocated_work = {}  # Track unallocated work

    for state, hours_needed in state_workloads.items():
        while hours_needed > 0:
            # Find staff licensed in the state and with available hours
            available_staff = [s for s in staff_licenses if state in staff_licenses[s] and staff_hours[s] < 40]

            if not available_staff:
                unallocated_work[state] = unallocated_work.get(state, 0) + hours_needed
                break

            # Distribute workload evenly among available staff
            hours_per_staff = min(hours_needed // len(available_staff), 40)
            for staff in available_staff:
                allocated_hours = min(hours_per_staff, 40 - staff_hours[staff])
                staff_hours[staff] += allocated_hours
                staff_allocations[staff][state] = staff_allocations[staff].get(state, 0) + allocated_hours
                hours_needed -= allocated_hours

    return staff_allocations, unallocated_work


# Streamlit interface
st.title("Work Allocation App")

# Define columns for layout
col1, col2 = st.columns(2)

# Worker's Licensing Information
with col1:
    st.subheader("Staff Licensing")
    staff_licenses = {}
    staff_num = st.number_input('Number of Staff Members', min_value=1, max_value=20, value=5)
    for i in range(staff_num):
        staff_name = st.text_input(f'Staff {i+1} Name', value=f'Staff {i+1}', key=f'staff_{i}_name')
        licenses = st.multiselect(f'{staff_name} - Licensed States', states, key=f'staff_{i}_licenses')
        staff_licenses[staff_name] = licenses

# States' Workload Information
with col2:
    st.subheader("State Workloads")
    state_workloads = {}
    state_num = st.number_input('Number of States with Workloads', min_value=1, max_value=len(states), value=3)
    for i in range(state_num):
        state = st.selectbox(f'State {i+1}', states, key=f'state_{i}')
        hours = st.number_input(f'{state} - Workload Hours', min_value=0, max_value=1000, value=40, key=f'hours_{i}')
        state_workloads[state] = hours

# Allocate work and display results
if st.button('Allocate Work'):
    allocations, unallocated_work = allocate_work(staff_licenses, state_workloads)
    
    # Results of Work Allocation
    st.subheader("Allocation Results")
    df = pd.DataFrame([(staff, state, hours) for staff, states in allocations.items() for state, hours in states.items()],
                      columns=['Staff', 'State', 'Allocated Hours'])
    st.table(df)

    # Warning for Unallocated Work
    if unallocated_work:
        st.warning("Warning: Not all work could be allocated. Unallocated work details:")
        for state, hours in unallocated_work.items():
            st.write(f"{state}: {hours} hours")
