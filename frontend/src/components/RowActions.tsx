interface RowActionsProps {
  onEdit: () => void;
  onDelete: () => void;
}

export default function RowActions({ onEdit, onDelete }: RowActionsProps) {
  return (
    <div className="table-actions">
      <button type="button" className="btn btn-secondary btn-sm" onClick={onEdit}>Edit</button>
      <button type="button" className="btn btn-danger btn-sm" onClick={onDelete}>Delete</button>
    </div>
  );
}
