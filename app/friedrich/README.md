# Friedrich
## Quote Sync
Friedrich Quotes can be synced to this service directly from the Friedrich Quotes 
Portal using the quote sync POST/PATCH endpoints `/vendors/friedrich/sync/local/quotes`
and the required secret.

Endpoints for syncing local state with the Friedrich Portal have been defined but have 
not been implemented.
  
The sync process makes every attempt at leveraging `async` to keep the runtime down,
but even still the entire process takes **1-2 minutes** for ~30 project quotes.

The status of sync operations will be made available upon a GET request to 
`vendors/friedrich/sync/status`, and with a session token, any state changes since
the last status check made.

Modifying resources are meant to be hit by some process implementing a polling 
cadence defined outside of this application.