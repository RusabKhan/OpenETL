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
  registered: {
    [key: string]: [];
  };
};

export type WorkerStatus = {
  active_workers?: {
    [key: string]: [];
  };
  reserved_tasks?: {
    [key: string]: [];
  };
  scheduled_tasks?: {
    [key: string]: [];
  };
  registered_tasks?: {
    [key: string]: [];
  };
};