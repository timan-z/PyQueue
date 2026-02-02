/* NOTE: Remember that for the data transfer (serialization/deserialization) into TypeScript, the fields
must match exactly. I faced this problem here since the fields in my Task class in Java were camelCase while
the fields here (types.ts) were PascalCase. Pretty sure TypeScript/JavaScript are supposed to actually be camelCase
too, but Go is a little weird with its casing standards, so I made the fields below PascalCase. Obv, I've reverted
that now and it seems to have fixed all of the issues I had with frontend-to-backend connectivity (only the data
retrieval functions weren't working).
*/
export type Task = {
    id: string;
    payload: string;
    type: string;
    status: string;
    attempts: number;
    maxRetries: number;
    createdAt: string;
}