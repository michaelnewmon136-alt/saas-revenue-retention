with source as (

    select * from {{ source('raw', 'invoices') }}

),

cleaned as (

    select
        invoice_id,
        account_id,
        cast(invoice_date as date) as invoice_date,
        amount as invoiced_amount,
        lower(trim(billing_cycle)) as billing_cycle,
        attempt,
        lower(trim(status)) as status,
        lower(trim(status)) = 'paid' as is_paid,
        case when lower(trim(status)) = 'paid' then amount else 0 end as cash_amount
    from source

)

select * from cleaned