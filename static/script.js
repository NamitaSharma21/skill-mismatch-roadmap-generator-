function generateRoadmap() {
  alert("🚀 Your roadmap will be generated soon!");
}
async function generateRoadmap() {
  // Ye data tum form ya dropdown se le sakti ho
  const role = document.getElementById("role").value;   // Example: dropdown
  const skills = ["HTML", "CSS"]; // Example: static list, later user input se

  const res = await fetch("http://127.0.0.1:5000/api/roadmap", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      target_role: role,
      skills: skills
    })
  });

  const data = await res.json();
  alert("🚀 Roadmap Generated!\n\n" + data.roadmap);
  console.log(data);
}
