SELECT
    it.typeID,
    it.typeName,
    dta.valueFloat as rank,
    it.description,
    ig.groupName,
    ig.groupID,
    it.published
FROM invTypes it
JOIN invGroups ig ON (it.groupID = ig.groupID)
JOIN dgmTypeAttributes dta ON (it.typeID = dta.typeID)
WHERE
    ig.categoryID = 16
    AND dta.attributeID = 275
    AND dta.valueFloat IS NOT NULL
    AND it.marketGroupID IS NOT NULL
