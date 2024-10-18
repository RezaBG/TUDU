import "./App.css";
import TodoList from "./components/TodoList.tsx";

function App() {
  const todos = [
    { id: 1, title: "Learn React", description: "Learn React" },
    { id: 2, title: "Learn TypeScript", description: "Learn TS" },
    { id: 3, title: "Build Todo App", description: "TUDU app" },
  ];

  const handleAddTodo = () => {};

  return (
    <>
      <h1>My Todo App</h1>
      <button onClick={handleAddTodo}>Add Todo</button>
      <TodoList todos={todos} />
    </>
  );
}

export default App;
