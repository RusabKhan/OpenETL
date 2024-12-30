import { ApiAuthParams, DatabaseAuthParams } from "./auth_params";

export type Connection = {
  id: string;
  connection_name: string;
  connection_type: string;
  connector_name: string;
  auth_type: string;
  connection_credentials: DatabaseAuthParams | ApiAuthParams;
  logo?: string;
};

export type ParamUpdateConnection = {
  document_id: string;
  fields: {
    [key: string]: string;
  };
};

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

export type MetadataConfig = {
  [schema: string]: string[];
};

export type TestConnection = {
  auth_type: string;
  connector_name: string;
  connector_type: string;
  auth_params: DatabaseAuthParams | ApiAuthParams;
};

export type StoreConnectionsParam = {
  connection_credentials: DatabaseAuthParams | ApiAuthParams;
  connector_name: string;
  auth_type: string;
  connection_name: string;
  connection_type: string;
};

export type GetCreatedConnections = {
  connection_name: string;
  connection_type: string;
  auth_type: string;
  connector_name: string;
  connection_credentials: DatabaseAuthParams | ApiAuthParams;
  id: number;
};
