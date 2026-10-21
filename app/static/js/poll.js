const polls = document.querySelectorAll(".pie_chart"); 

for (const poll of polls) {
    const labels = Function(`return ${poll.dataset.poll_labels}`)(); // Converts camelCase automatically
    const data = Function(`return ${poll.dataset.poll_data}`)();

    console.log(poll);

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