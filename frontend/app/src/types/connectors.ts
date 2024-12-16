import { ApiAuthParams, DatabaseAuthParams } from "./auth_params";

export type Connectors = {
  database: string[];
  api: string[];
};

export type ParamMetadata = {
  auth_options: {
    auth_type: {
      name: string;
      value: string;
    };
    connection_credentials: DatabaseAuthParams | ApiAuthParams;
    connection_name: string;
    connection_type: string;
    connector_name: string;
  };
  connector_name: string;
  connector_type: string;
};

export type Metadata = {
  [schema: string]: string[];
}