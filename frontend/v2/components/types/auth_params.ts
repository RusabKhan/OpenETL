export type DatabaseAuthParams = {
  hostname: string;
  database: string;
  username: string;
  password: string;
  port: number;
};

export type ApiAuthParams = {
  token: string;
};

export type LoginFormParam = {
  username: string;
  password: string;
};

export type CreateUserForm = {
  username: string;
  password: string;
  permissions: string[];
};

export type CreateUserDetails = {
  id: string;
  username: string;
  password: string;
  permissions: string[];
  created_at: string;
  updated_at: string;
};
