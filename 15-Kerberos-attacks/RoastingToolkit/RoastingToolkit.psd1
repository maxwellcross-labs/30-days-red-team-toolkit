@{
    RootModule        = 'RoastingToolkit.psm1'
    ModuleVersion     = '1.0.0'
    Author            = 'Maxwell Cross'
    Description       = 'Quick Kerberoasting & AS-REP Roasting from Windows — enumeration, extraction, and hash output.'

    FunctionsToExport = @(
        'Find-RoastableAccounts',
        'Invoke-QuickKerberoast',
        'Invoke-QuickASREPRoast'
    )

    CmdletsToExport   = @()
    VariablesToExport  = @()
    AliasesToExport    = @()
}