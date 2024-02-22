        // Function to toggle the visibility of the stacked switch
        function toggleStackedSwitch() {
            var kdeCheckbox = document.querySelector('input[name="kde_graph"]');
            var stackedSwitchContainer = document.querySelector('[data-stacked-switch]');

            // Check if the KDE checkbox is checked
            if (kdeCheckbox.checked) {
                stackedSwitchContainer.style.display = 'flex'; // Show the switch
            } else {
                stackedSwitchContainer.style.display = 'none'; // Hide the switch
            }
        }

        // Attach an event listener to the KDE checkbox to toggle the switch on change
        document.addEventListener('DOMContentLoaded', function () {
            var kdeCheckbox = document.querySelector('input[name="kde_graph"]');
            kdeCheckbox.addEventListener('change', toggleStackedSwitch);

            // Call the function initially to set the initial state
            toggleStackedSwitch();
        });