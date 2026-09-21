import type { components } from "@/lib/api/schema"

type Schemas = components["schemas"]

export type ApiSneaker = Schemas["SneakerResponse"]
export type ApiSneakerRequest = Schemas["SneakerRequest"]
export type ApiColorway = Schemas["ColorwayResponse"]
export type ApiImage = Schemas["ImageResponse"]
export type ApiGender = Schemas["Gender"]
export type ApiSneakerStatus = Schemas["SneakerStatus"]
export type ApiCatalogFacets = Schemas["CatalogFacetsResponse"]
export type ApiBrandRequest = Schemas["BrandRequest"]
export type ApiCategoryRequest = Schemas["CategoryRequest"]
export type ApiColorwayRequest = Schemas["ColorwayRequest"]
export type ApiSneakerSort = Schemas["SneakerSort"]
export type ApiUser = Schemas["UserResponse"]
export type ApiRole = Schemas["Role"]
export type ApiCreateUserRequest = Schemas["CreateUserRequest"]
export type ApiUpdateUserRequest = Schemas["UpdateUserRequest"]
