// static/js/script.js
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("homeTeamsBtn").addEventListener("click", function() {
        fetch('/teams?type=home')
            .then(response => response.text())
            .then(data => {
                document.getElementById("homeTeams").style.display = "block";
                document.getElementById("homeTeams").innerHTML = data;
                document.getElementById("yr").style.display = "none"; // Hide the away teams container
            });
    });

    document.getElementById("yrb").addEventListener("click", function() {
        fetch('/teams?type=year')
            .then(response => response.text())
            .then(data => {
                document.getElementById("yr").style.display = "block";
                document.getElementById("yr").innerHTML = data;
                document.getElementById("homeTeams").style.display = "none"; // Hide the home teams container
            });
    });



});
