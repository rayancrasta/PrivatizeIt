from validaton import fetch_masking_schema

async def masking_record(detokenised_dict,masking_policy_id) -> dict:
    try:
        schema = await fetch_masking_schema(masking_policy_id)
    except Exception as e:
        raise "Error fetching masking schema"
    
    try:
        rule_fields = [rule.field_name for rule in schema.rules]
        
        masked_record = {}
        
        for key,value in detokenised_dict.items():
            if key in rule_fields:
                #Find the matching rule 
                matching_rule = next((rule for rule in schema.rules if rule.field_name == key),None)
                if matching_rule:
                    # print(matching_rule)
                    # print(type(matching_rule))
                    show_start = matching_rule.show_start
                    show_last = matching_rule.show_last

                    #Calculate number of elements to X
                    xnum = len(value) - (show_start+show_last)
                    
                    if xnum > 0:
                        masked_value = value[:show_start] + 'X'*xnum + value[-show_last:]
                    else:
                        masked_value = value #value is too short to mask
                    masked_record[key]=masked_value
                else:
                    masked_record[key]=value
            else:
                masked_record[key]=value
        
        return masked_record
    except Exception as e:
        raise "Error masking the record"