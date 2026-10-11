const container = document.getElementById('options_container');
const add_button = document.getElementById('add_option_button');

add_button.addEventListener('click', function() {
    const input_label = document.createElement('label');
    // input_label.classList.add()
    // for later

    const new_input = document.createElement('input');
    new_input.name = 'option';
    new_input.type = 'text';
    new_input.placeholder = 'Enter Option Text';

    const new_div = document.createElement('div')
    new_div.classList.add('row')

    const new_button = document.createElement('button');
    new_button.textContent = 'Remove Option';
    new_button.addEventListener('click', function() {
        container.removeChild(new_button.parentElement.parentElement)
    });

    new_div.appendChild(new_input);
    new_div.appendChild(new_button);

    input_label.appendChild(new_div);

    container.appendChild(input_label);
});

const public_switch = document.getElementById('public_switch');
const participant_range = document.getElementById('participant_range');
const range_output = document.getElementById('range_output');

public_switch.addEventListener('input', function() {
    participant_range.disabled = public_switch.checked
    if (public_switch.checked) range_output.textContent = '-'
    else range_output.textContent = participant_range.value
});

participant_range.addEventListener('input', function() {
    range_output.textContent = participant_range.value
});