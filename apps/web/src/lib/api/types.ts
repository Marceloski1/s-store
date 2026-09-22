import type {
  components,
  Currency,
  Gender,
  Role,
  SneakerSort,
  SneakerStatus,
} from "@/lib/api/schema"

export {
  Currency,
  ErrorCode,
  Gender,
  Role,
  SneakerSort,
  SneakerStatus,
} from "@/lib/api/schema"

type Schemas = components["schemas"]

export type ApiSneaker = Schemas["SneakerResponse"]
export type ApiSneakerRequest = Schemas["SneakerRequest"]
export type ApiColorway = Schemas["ColorwayResponse"]
export type ApiImage = Schemas["ImageResponse"]
export type ApiGender = Gender
export type ApiSneakerStatus = SneakerStatus
export type ApiCatalogFacets = Schemas["CatalogFacetsResponse"]
export type ApiBrandRequest = Schemas["BrandRequest"]
export type ApiCategoryRequest = Schemas["CategoryRequest"]
export type ApiColorwayRequest = Schemas["ColorwayRequest"]
export type ApiSneakerSort = SneakerSort
export type ApiUser = Schemas["UserResponse"]
export type ApiRole = Role
export type ApiCreateUserRequest = Schemas["CreateUserRequest"]
export type ApiUpdateUserRequest = Schemas["UpdateUserRequest"]
export type ApiCurrency = Currency
