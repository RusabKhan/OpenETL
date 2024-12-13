import { ApiAuthParams, DatabaseAuthParams } from "./auth_params";

export type TestConnection = {
  auth_type: string;
  connector_name: string;
  connector_type: string;
  auth_params: DatabaseAuthParams | ApiAuthParams;
};
