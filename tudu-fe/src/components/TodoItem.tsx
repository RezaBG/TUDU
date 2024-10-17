interface TodoItemProps {
  title: string;
  description: string;
}

const TodoItem = ({ title, description }: TodoItemProps) => {
  return (
    <div className="todo-item">
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
};

export default TodoItem;
