-- Steal An Egg - Dropdown Selection & Auto Steal Hub
local Players = game:GetService("Players")
local LocalPlayer = Players.LocalPlayer
local PlayerGui = LocalPlayer:WaitForChild("PlayerGui")

if PlayerGui:FindFirstChild("EggHubGui") then
    PlayerGui.EggHubGui:Destroy()
end

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "EggHubGui"
ScreenGui.Parent = PlayerGui
ScreenGui.ResetOnSpawn = false

-- النافذة الرئيسية
local MainFrame = Instance.new("Frame")
MainFrame.Parent = ScreenGui
MainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 25)
MainFrame.Position = UDim2.new(0.3, 0, 0.2, 0)
MainFrame.Size = UDim2.new(0, 260, 0, 360)
MainFrame.Active = true
MainFrame.Draggable = true

-- عنوان القائمة
local Title = Instance.new("TextLabel")
Title.Parent = MainFrame
Title.BackgroundColor3 = Color3.fromRGB(10, 10, 15)
Title.Size = UDim2.new(1, 0, 0, 40)
Title.Text = "Steal An Egg - Target Hub 🚀"
Title.TextColor3 = Color3.fromRGB(255, 255, 255)
Title.TextSize = 16
Title.Font = Enum.Font.SourceSansBold

-- عنوان الاختيار
local TargetLabel = Instance.new("TextLabel")
TargetLabel.Parent = MainFrame
TargetLabel.BackgroundTransparency = 1
TargetLabel.Position = UDim2.new(0.1, 0, 0.13, 0)
TargetLabel.Size = UDim2.new(0.8, 0, 0, 20)
TargetLabel.Text = "اختر الحيوان/البيضة المستهدفة:"
TargetLabel.TextColor3 = Color3.fromRGB(180, 180, 180)
TargetLabel.TextSize = 13
TargetLabel.Font = Enum.Font.SourceSans

-- زر القائمة المنسدلة (Dropdown)
local DropdownBtn = Instance.new("TextButton")
DropdownBtn.Parent = MainFrame
DropdownBtn.BackgroundColor3 = Color3.fromRGB(35, 35, 45)
DropdownBtn.Position = UDim2.new(0.1, 0, 0.20, 0)
DropdownBtn.Size = UDim2.new(0.8, 0, 0, 35)
DropdownBtn.Text = "اختر من القائمة... ▼"
DropdownBtn.TextColor3 = Color3.fromRGB(0, 255, 150)
DropdownBtn.TextSize = 14
DropdownBtn.Font = Enum.Font.SourceSansBold

-- إطار خيارات القائمة المنسدلة
local DropdownList = Instance.new("ScrollingFrame")
DropdownList.Parent = MainFrame
DropdownList.BackgroundColor3 = Color3.fromRGB(28, 28, 38)
DropdownList.Position = UDim2.new(0.1, 0, 0.31, 0)
DropdownList.Size = UDim2.new(0.8, 0, 0, 110)
DropdownList.Visible = false
DropdownList.CanvasSize = UDim2.new(0, 0, 2, 0)
DropdownList.ScrollBarThickness = 5

local UIListLayout = Instance.new("UIListLayout")
UIListLayout.Parent = DropdownList
UIListLayout.SortOrder = Enum.SortOrder.LayoutOrder

-- زر التحديث (Refresh Eggs)
local RefreshBtn = Instance.new("TextButton")
RefreshBtn.Parent = MainFrame
RefreshBtn.BackgroundColor3 = Color3.fromRGB(45, 45, 60)
RefreshBtn.Position = UDim2.new(0.1, 0, 0.65, 0)
RefreshBtn.Size = UDim2.new(0.8, 0, 0, 32)
RefreshBtn.Text = "Refresh Eggs List 🔄"
RefreshBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
RefreshBtn.TextSize = 13
RefreshBtn.Font = Enum.Font.SourceSansBold

-- زر السرقة التلقائية (Auto Steal)
local AutoStealBtn = Instance.new("TextButton")
AutoStealBtn.Parent = MainFrame
AutoStealBtn.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
AutoStealBtn.Position = UDim2.new(0.1, 0, 0.76, 0)
AutoStealBtn.Size = UDim2.new(0.8, 0, 0, 38)
AutoStealBtn.Text = "Auto Steal: [OFF]"
AutoStealBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
AutoStealBtn.TextSize = 15
AutoStealBtn.Font = Enum.Font.SourceSansBold

-- زر منطقة الأمان
local SafeZoneBtn = Instance.new("TextButton")
SafeZoneBtn.Parent = MainFrame
SafeZoneBtn.BackgroundColor3 = Color3.fromRGB(50, 120, 200)
SafeZoneBtn.Position = UDim2.new(0.1, 0, 0.88, 0)
SafeZoneBtn.Size = UDim2.new(0.8, 0, 0, 32)
SafeZoneBtn.Text = "العودة لمنطقة الأمان 🛡️"
SafeZoneBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
SafeZoneBtn.TextSize = 13
SafeZoneBtn.Font = Enum.Font.SourceSansBold

-- ==========================================
-- منطق تحديث القائمة والسرقة التلقائية
-- ==========================================

local selectedTargetName = ""
local autoStealActive = false

-- وظيفة فحص وتعبئة عناصر القائمة من الماب
local function updateEggList()
    -- تفريغ العناصر القديمة
    for _, child in ipairs(DropdownList:GetChildren()) do
        if child:IsA("TextButton") then
            child:Destroy()
        end
    end

    local addedNames = {}
    
    -- البحث في الماب عن أجزاء البيض والحيوانات
    for _, obj in ipairs(workspace:GetDescendants()) do
        local objName = obj.Name
        local nameLower = objName:lower()
        
        if (nameLower:find("egg") or nameLower:find("nest") or nameLower:find("secret") or nameLower:find("divine") or nameLower:find("mythical")) and not addedNames[objName] then
            addedNames[objName] = true
            
            local OptionBtn = Instance.new("TextButton")
            OptionBtn.Parent = DropdownList
            OptionBtn.Size = UDim2.new(1, 0, 0, 25)
            OptionBtn.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
            OptionBtn.Text = objName
            OptionBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
            OptionBtn.TextSize = 12
            OptionBtn.Font = Enum.Font.SourceSans
            
            OptionBtn.MouseButton1Click:Connect(function()
                selectedTargetName = objName
                DropdownBtn.Text = objName .. " ▼"
                DropdownList.Visible = false
            end)
        end
    end
end

-- إظهار/إخفاء القائمة المنسدلة
DropdownBtn.MouseButton1Click:Connect(function()
    DropdownList.Visible = not DropdownList.Visible
    if DropdownList.Visible then
        updateEggList()
    end
end)

-- زر التحديث
RefreshBtn.MouseButton1Click:Connect(function()
    updateEggList()
    RefreshBtn.Text = "Refreshed! ✅"
    task.wait(1)
    RefreshBtn.Text = "Refresh Eggs List 🔄"
end)

-- زر السرقة التلقائية للهدف المختار
AutoStealBtn.MouseButton1Click:Connect(function()
    autoStealActive = not autoStealActive
    
    if autoStealActive then
        AutoStealBtn.Text = "Auto Steal: [ON]"
        AutoStealBtn.BackgroundColor3 = Color3.fromRGB(50, 200, 80)
        
        task.spawn(function()
            while autoStealActive do
                local char = LocalPlayer.Character
                if char and char:FindFirstChild("HumanoidRootPart") then
                    local foundTarget = nil
                    
                    -- البحث عن العنصر المحدد من القائمة
                    if selectedTargetName ~= "" then
                        for _, obj in ipairs(workspace:GetDescendants()) do
                            if obj.Name == selectedTargetName then
                                if obj:IsA("Model") and obj.PrimaryPart then
                                    foundTarget = obj.PrimaryPart
                                    break
                                elseif obj:IsA("BasePart") then
                                    foundTarget = obj
                                    break
                                end
                            end
                        end
                    end
                    
                    -- إذا لم يحدد حيواناً معيناً ينقل لأول بيضة متاحة
                    if not foundTarget then
                        for _, obj in ipairs(workspace:GetDescendants()) do
                            local nameLower = obj.Name:lower()
                            if nameLower:find("egg") or nameLower:find("nest") then
                                if obj:IsA("Model") and obj.PrimaryPart then
                                    foundTarget = obj.PrimaryPart
                                    break
                                elseif obj:IsA("BasePart") then
                                    foundTarget = obj
                                    break
                                end
                            end
                        end
                    end
                    
                    if foundTarget then
                        char.HumanoidRootPart.CFrame = foundTarget.CFrame + Vector3.new(0, 3, 0)
                    end
                end
                task.wait(1.5)
            end
        end)
    else
        AutoStealBtn.Text = "Auto Steal: [OFF]"
        AutoStealBtn.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
    end
end)

-- زر منطقة الأمان
SafeZoneBtn.MouseButton1Click:Connect(function()
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("HumanoidRootPart") then
        local spawn = workspace:FindFirstChild("SpawnLocation") or workspace:FindFirstChild("Spawn")
        if spawn then
            char.HumanoidRootPart.CFrame = spawn.CFrame + Vector3.new(0, 3, 0)
        else
            char.HumanoidRootPart.CFrame = CFrame.new(0, 10, 0)
        end
    end
end)

-- تحديث الأهداف فور تشغيل السكربت
updateEggList()
