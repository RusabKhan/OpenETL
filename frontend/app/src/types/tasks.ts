export type WorkerTasks = {
  active_tasks: {
    [key: string]: [];
  };
  reserved_tasks: {
    [key: string]: [];
  };
  scheduled_tasks: {
    [key: string]: [];
  };
};
