document.addEventListener('DOMContentLoaded', function() {
  // Function to change login form IDs
  function changeLoginIds(anchorId) {
        var btn = document.getElementById('position-sm')
        var loginH3 = document.getElementById('login');
        var position = document.getElementById('position');
        // Change IDs based on anchor clicks
        loginH3.innerHTML = anchorId + " Login";
        position.value = anchorId;
        btn.innerText = anchorId
        console.log(btn);
        console.log(btn.innerHTML);

    }

    // Anchor click event listeners
    var anchor1 = document.getElementById('staff');
    var anchor2 = document.getElementById('manager');
    var anchor3 = document.getElementById('principal');  
    
    // Anchor click event listeners
    var list1 = document.getElementById('staff-sm');
    var list2 = document.getElementById('manager-sm');
    var list3 = document.getElementById('principal-sm');

    anchor1.addEventListener('click', function(e) {
        e.preventDefault(); // Prevent default anchor behavior
        document.title = "Employee Login"
        changeLoginIds('Employee');
        console.log("Employee")
      });
      
      anchor2.addEventListener('click', function(e) {
        e.preventDefault(); // Prevent default anchor behavior
        document.title = "Reporting Manager Login"
        changeLoginIds('Manager');
        console.log("manager")
      });
      
      anchor3.addEventListener('click', function(e) {
        e.preventDefault(); // Prevent default anchor behavior
        document.title = "Principal Login"
        changeLoginIds('Principal');
        console.log("principal")
    });
    
    list1.addEventListener('click', function(e) {
        e.preventDefault(); // Prevent default anchor behavior
        document.title = "Employee Login"
        changeLoginIds('Employee');
        console.log("Employee")
      });
      
      list2.addEventListener('click', function(e) {
        e.preventDefault(); // Prevent default anchor behavior
        document.title = "Reporting Manager Login"
        changeLoginIds('Manager');
        console.log("manager")
      });
      
      list3.addEventListener('click', function(e) {
        e.preventDefault(); // Prevent default anchor behavior
        document.title = "Principal Login"
        changeLoginIds('Principal');
        console.log("principal")
    });
});