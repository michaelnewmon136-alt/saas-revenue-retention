with source as (

    select * from {{ source('raw', 'accounts') }}

),

cleaned as (

    select
        account_id,
        case
            when lower(trim(segment)) in ('smb', 'small business') then 'SMB'
            when lower(trim(segment)) in ('mid-market', 'mid market') then 'Mid-Market'
            when lower(trim(segment)) = 'enterprise' then 'Enterprise'
            else 'Unknown'
        end as segment,
        coalesce(industry, 'Unknown') as industry,
        channel,
        cast(signup_date as date) as signup_date
    from source

),

deduplicated as (

    select distinct * from cleaned

)

select * from deduplicated