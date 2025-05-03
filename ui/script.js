// script.js

document.addEventListener('DOMContentLoaded', () => {
  const fetchButton = document.getElementById('fetch-button');

  fetchButton.addEventListener('click', async () => {
    try {
      const response = await fetch('https://api.example.com/data');
      if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
      }
      const data = await response.json();
      console.log(data);
    } catch (error) {
      console.error('There has been a problem with your fetch operation:', error);
    }
  });
});