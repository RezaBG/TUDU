import TodoItem from "./TodoItem.tsx";

interface Todo {
  id: number;
  title: string;
  description: string;
}

interface TodoListProps {
  todos: Todo[];
}

const TodoList = ({ todos }: TodoListProps) => {
  return (
    <div>
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          title={todo.title}
          description={todo.description}
        />
      ))}
    </div>
  );
};

export default TodoList;
