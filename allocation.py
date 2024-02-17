import streamlit as st
import pandas as pd

import pulp
def allocate_work(staff_licenses, state_workloads, hours, weeks, switch_penalty=1):
    limit = hours * weeks  # Total hours available for work

    # Create the 'prob' variable to contain the problem data
    prob = pulp.LpProblem("Staff Allocation Problem", pulp.LpMinimize)

    # Create decision variables
    staff_hours = pulp.LpVariable.dicts("StaffHours", 
                                        ((staff, state) for staff in staff_licenses for state in staff_licenses[staff]),
                                        lowBound=0, 
                                        cat='Continuous')

    # Create slack variables
    slack = pulp.LpVariable.dicts("Slack", state_workloads.keys(), lowBound=0, cat='Continuous')

    # Create binary variables for state switches
    switches = pulp.LpVariable.dicts("Switches", 
                                     ((staff, state) for staff in staff_licenses for state in staff_licenses[staff]),
                                     cat='Binary')

    # Objective function: Minimize the total slack and the total number of state switches
    prob += pulp.lpSum(slack.values()) + switch_penalty * pulp.lpSum(switches.values())

    # Constraints
    for staff in staff_licenses:
        prob += pulp.lpSum([staff_hours[(staff, state)] for state in staff_licenses[staff]]) <= limit, f"HourLimit_{staff}"

    for state, hours_needed in state_workloads.items():
        prob += pulp.lpSum([staff_hours[(staff, state)] for staff in staff_licenses if state in staff_licenses[staff]]) + slack[state] >= hours_needed, f"Workload_{state}"

    # Additional constraints to link the binary variables with the decision variables
    for staff in staff_licenses:
        for state in staff_licenses[staff]:
            prob += staff_hours[(staff, state)] <= limit * switches[(staff, state)], f"Switch_{staff}_{state}"

    # Solve the problem
    status = prob.solve()

    # Prepare the results
    staff_allocations = {staff: {state: staff_hours[(staff, state)].varValue for state in staff_licenses[staff]} for staff in staff_licenses}
    unallocated_work = {state: slack[state].varValue for state in state_workloads}

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

st.markdown('---')

st.write("Enter Staff Licenses:")
staff_licenses = {}
staff_num = st.number_input('Number of staff members', min_value=1, max_value=20, value=5)
default_staff_licenses = [['Arizona', 'Texas'], ['Texas', 'Florida', 'New York'], ['New York', 'Texas'], ['Arizona', 'Texas'], ['Florida']]
for i in range(staff_num):
    col1, col2 = st.columns([2, 3])
    with col2:
        # If there are more than 5 workers, default to no state allocation
        default_licenses = default_staff_licenses[i] if i < 5 else []
        licenses = st.multiselect(f'Select states for Staff {i+1}', states, default=default_licenses, key=f'staff_{i}_licenses')
    with col1:
        staff_name = st.text_input(f'Staff member {i+1} name', value=f'Staff {i+1}', key=f'staff_{i}_name')
    staff_licenses[staff_name] = licenses

st.markdown('---')

# Dynamic input for state workloads
st.write("Enter State Workloads:")
state_workloads = {}
state_num = st.number_input('Number of states to enter workloads for', min_value=1, max_value=len(states), value=4)
default_state_workloads = [('Florida', 80), ('Arizona', 120), ('New York', 80), ('Texas', 320)]
for i in range(state_num):
    col1, col2 = st.columns([1, 1])
    with col2:
        # If there are more than 4 states, default to 0 hours
        default_hours = default_state_workloads[i][1] if i < 4 else 0
        hours = st.number_input(f'Hours for State {i+1}', min_value=0, max_value=1000, value=default_hours, key=f'hours_{i}')
    with col1:
        state = st.selectbox(f'State {i+1}', states, index=states.index(default_state_workloads[i][0]) if i < 4 else 0, key=f'state_{i}')
    state_workloads[state] = hours

st.markdown('---')

# Button to perform allocation
if st.button('Allocate Work'):
    allocations, unallocated_work = allocate_work(staff_licenses, state_workloads, work_hours_per_week, num_weeks)
    
    # Displaying the results in a table
    st.write("Allocation Results:")
    df = pd.DataFrame([(staff, state, hours) for staff, states in allocations.items() for state, hours in states.items()],
                      columns=['Staff', 'State', 'Allocated Hours'])
    df = df[df['Allocated Hours'] > 0]
    st.table(df)

    # Display warning if there is unallocated work
    if sum(unallocated_work.values()) > 0:
        st.warning("Warning: Not all work could be allocated due to insufficient or unavailable staff. Unallocated work:")
        for state, hours in unallocated_work.items():
            if hours > 0:
                st.write(f"{state}: {hours} hours")
