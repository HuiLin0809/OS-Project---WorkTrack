document.getElementById('checkInBtn').addEventListener('click', function () {
    const empId = document.getElementById('empId').value;
    const empName = document.getElementById('empName').value;
    const statusMessage = document.getElementById('statusMessage');

    // Make sure the user didn't leave the fields blank
    if (!empId || !empName) {
        statusMessage.innerHTML = "<span class='error'>Please enter both ID and Name.</span>";
        return;
    }

    statusMessage.innerHTML = "Getting location...";

    // 1. Get GPS coordinates 
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;

                // 2. Get current timestamp 
                // Format it nicely so the database can read it (YYYY-MM-DD HH:MM:SS)
                const now = new Date();
                const timestamp = now.toISOString().slice(0, 19).replace('T', ' ');

                // Bundle all the data together
                const checkInData = {
                    empId: empId,
                    empName: empName,
                    latitude: latitude,
                    longitude: longitude,
                };

                statusMessage.innerHTML = "Sending data to server...";

                // 3. Send data via fetch() POST request 
                fetch('https://overlook-reapply-trophy.ngrok-free.dev/api/checkin', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(checkInData)
                })
                    .then(response => {
                        if (response.ok) {
                            // 4. Show success message 
                            statusMessage.innerHTML = "<span class='success'>Check-in successful!</span>";
                        } else {
                            statusMessage.innerHTML = "<span class='error'>Check-in failed on server.</span>";
                        }
                    })
                    .catch(error => {
                        // This error will show up right now because we don't have a server yet!
                        statusMessage.innerHTML = "<span class='error'>Error connecting to server. (Expected until backend is ready)</span>";
                        console.error('Network Error:', error);
                    });
            },
            function (error) {
                // If the user denies location permissions
                statusMessage.innerHTML = "<span class='error'>Please allow location access to check in.</span>";
            }
        );
    } else {
        statusMessage.innerHTML = "<span class='error'>Geolocation is not supported by your browser.</span>";
    }
});