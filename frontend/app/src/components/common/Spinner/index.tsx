const Spinner = () => {
  return (
    <div>
      <div
        className="h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary border-t-transparent"
        role="status"
      ></div>
    </div>
  );
};

export default Spinner;
