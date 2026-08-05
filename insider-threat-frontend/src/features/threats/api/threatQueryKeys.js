export const threatQueryKeys = {
  all: ["threats"],

  lists: () => [...threatQueryKeys.all, "list"],

  list: (filters = {}) => [
    ...threatQueryKeys.lists(),
    filters,
  ],

  details: () => [...threatQueryKeys.all, "detail"],

  detail: (id) => [
    ...threatQueryKeys.details(),
    id,
  ],
};
