// Get container and Button from the Page
const container = document.getElementById('options_container');
const add_button = document.getElementById('add_option_button');

// Add click event to the button
add_button.addEventListener('click', function() {
    // Create 'Span' Container with the class: "row"
    const input_span = document.createElement('span');
    input_span.classList.add("row")

    // Create a new text input for a poll option
    const new_input = document.createElement('input');
    new_input.name = 'option';
    new_input.type = 'text';
    new_input.placeholder = 'Enter Option Text';

    // Create a new remove button for the poll option with functionality
    // to delete the span and all its containing elements on click
    const new_button = document.createElement('button');
    new_button.textContent = 'Remove';
    new_button.type = "button";
    new_button.classList.add("red")
    new_button.addEventListener('click', function() {
        container.removeChild(new_button.parentElement)
    });

    // Add input and button as children of span
    input_span.appendChild(new_input);
    input_span.appendChild(new_button);

    // Add span as the child of the container
    container.appendChild(input_span);
});

// Get switch, range and range text output from the form
const public_switch = document.getElementById('public_switch');
const participant_range = document.getElementById('participant_range');
const range_output = document.getElementById('range_output');

// Add event to the checkbox
public_switch.addEventListener('input', function() {

    // if the switch is checked, disable the range
    participant_range.disabled = public_switch.checked

    // if the switch is checked, set the output to a empty character,
    // otherwise output the ranges value
    if (public_switch.checked) range_output.textContent = '-'
    else range_output.textContent = participant_range.value
});

// Add event to the range
participant_range.addEventListener('input', function() {

    // If the range is updated, update the output to the value of the range
    range_output.textContent = participant_range.value
});