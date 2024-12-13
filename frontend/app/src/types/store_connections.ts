import { ApiAuthParams, DatabaseAuthParams } from "./auth_params";

export type StoreConnections = {
  connection_credentials: DatabaseAuthParams | ApiAuthParams;
  connector_name: string;
  auth_type: string;
  connection_name: string;
  connection_type: string;
  [key: string]: any; // Index signature
};
