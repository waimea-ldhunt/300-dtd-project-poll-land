// Get all pie chart containers
const polls = document.querySelectorAll(".pie_chart"); 

// For each pie chart container
for (const poll of polls) {

  //Reads label and data inputs in the correct format
  const labels = Function(`return ${poll.dataset.poll_labels}`)();
  const data = Function(`return ${poll.dataset.poll_data}`)();

  //Creates a new pie chart with chart.js using the labels and data
  new Chart(poll, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: [
          'rgb(255 102 102)',
          'rgb(89 172 255)',
          'rgb(254, 214, 106)',
          'rgb(94, 222, 166)'
        ],
        borderWidth: 0,
        borderColor: 'transparent'
      }]
    },
    options: {
      plugins: {
        legend: {
          onClick: null,
          labels: {
            color: 'white',
            font: {
              weight: 'bold',
              size: 12
            }
          }
        }
      }
    }
  });
}