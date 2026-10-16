-- Steal An Egg - Monster Teleport & Fixed Spawn Hub 🚀
local Players = game:GetService("Players")
local CoreGui = game:GetService("CoreGui")
local LocalPlayer = Players.LocalPlayer

if CoreGui:FindFirstChild("EggHubGui") then
    CoreGui.EggHubGui:Destroy()
end

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "EggHubGui"
pcall(function() ScreenGui.Parent = CoreGui end)
if not ScreenGui.Parent then ScreenGui.Parent = LocalPlayer:WaitForChild("PlayerGui") end
ScreenGui.ResetOnSpawn = false

local MainFrame = Instance.new("Frame")
MainFrame.Parent = ScreenGui
MainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 25)
MainFrame.Position = UDim2.new(0.25, 0, 0.15, 0)
MainFrame.Size = UDim2.new(0, 280, 0, 390)
MainFrame.Active = true
MainFrame.Draggable = true

local Title = Instance.new("TextLabel")
Title.Parent = MainFrame
Title.BackgroundColor3 = Color3.fromRGB(10, 10, 15)
Title.Size = UDim2.new(1, 0, 0, 40)
Title.Text = "Monster Teleport Hub 🚀"
Title.TextColor3 = Color3.fromRGB(255, 255, 255)
Title.TextSize = 16
Title.Font = Enum.Font.SourceSansBold

-- دالة نقل تثبت الشخصية وتمنع الماب من إعادة سحبك
local function forceTeleport(targetCFrame)
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("HumanoidRootPart") then
        local root = char.HumanoidRootPart
        
        -- تصفير السرعات لفك ارتباط الحماية والسحب
        root.AssemblyLinearVelocity = Vector3.new(0, 0, 0)
        root.AssemblyAngularVelocity = Vector3.new(0, 0, 0)
        
        root.CFrame = targetCFrame
        task.wait(0.05)
        root.AssemblyLinearVelocity = Vector3.new(0, 0, 0)
    end
end

-- زر العودة للبداية المضمون (يمنع السحب التلقائي بعد المرحلة 5)
local SpawnBtn = Instance.new("TextButton")
SpawnBtn.Parent = MainFrame
SpawnBtn.BackgroundColor3 = Color3.fromRGB(50, 120, 200)
SpawnBtn.Position = UDim2.new(0.1, 0, 0.15, 0)
SpawnBtn.Size = UDim2.new(0.8, 0, 0, 40)
SpawnBtn.Text = "العودة للبداية / القاعدة 🛡️"
SpawnBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
SpawnBtn.TextSize = 14
SpawnBtn.Font = Enum.Font.SourceSansBold

SpawnBtn.MouseButton1Click:Connect(function()
    task.spawn(function()
        local spawnPart = workspace:FindFirstChild("SpawnLocation") or workspace:FindFirstChild("Spawn")
        local targetCF = spawnPart and (spawnPart.CFrame + Vector3.new(0, 4, 0)) or CFrame.new(0, 12, 0)
        
        -- التكرار لمدة قصيرة لمنع الماب من إعادتك للمرحلة المتقدمة
        for i = 1, 3 do
            forceTeleport(targetCF)
            task.wait(0.1)
        end
    end)
end)

-- قائمة المراحل
local worldList = {
    "Forest",
    "Lake",
    "Desert",
    "Jungle",
    "Snow",
    "Volcano",
    "Abyss Ocean",
    "Prehistoric",
    "Cosmic",
    "Cherry Blossom",
    "Titan Temple",
    "Demons",
    "Enchanted Forest"
}

local selectedWorld = "Forest"

local DropdownBtn = Instance.new("TextButton")
DropdownBtn.Parent = MainFrame
DropdownBtn.BackgroundColor3 = Color3.fromRGB(35, 35, 45)
DropdownBtn.Position = UDim2.new(0.1, 0, 0.32, 0)
DropdownBtn.Size = UDim2.new(0.8, 0, 0, 35)
DropdownBtn.Text = "اختر المرحلة: " .. selectedWorld .. " ▼"
DropdownBtn.TextColor3 = Color3.fromRGB(0, 255, 150)
DropdownBtn.TextSize = 13
DropdownBtn.Font = Enum.Font.SourceSansBold

local DropdownList = Instance.new("ScrollingFrame")
DropdownList.Parent = MainFrame
DropdownList.BackgroundColor3 = Color3.fromRGB(28, 28, 38)
DropdownList.Position = UDim2.new(0.1, 0, 0.44, 0)
DropdownList.Size = UDim2.new(0.8, 0, 0, 170)
DropdownList.Visible = false
DropdownList.CanvasSize = UDim2.new(0, 0, 3.5, 0)
DropdownList.ScrollBarThickness = 6

local UIListLayout = Instance.new("UIListLayout")
UIListLayout.Parent = DropdownList
UIListLayout.SortOrder = Enum.SortOrder.LayoutOrder

for _, wName in ipairs(worldList) do
    local opt = Instance.new("TextButton")
    opt.Parent = DropdownList
    opt.Size = UDim2.new(1, 0, 0, 30)
    opt.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
    opt.Text = wName
    opt.TextColor3 = Color3.fromRGB(255, 255, 255)
    opt.TextSize = 13
    opt.Font = Enum.Font.SourceSans
    
    opt.MouseButton1Click:Connect(function()
        selectedWorld = wName
        DropdownBtn.Text = "اختر المرحلة: " .. wName .. " ▼"
        DropdownList.Visible = false
    end)
end

DropdownBtn.MouseButton1Click:Connect(function()
    DropdownList.Visible = not DropdownList.Visible
end)

-- زر الانتقال المباشر لمركز المرحلة عند الوحش
local TeleportWorldBtn = Instance.new("TextButton")
TeleportWorldBtn.Parent = MainFrame
TeleportWorldBtn.BackgroundColor3 = Color3.fromRGB(80, 180, 80)
TeleportWorldBtn.Position = UDim2.new(0.1, 0, 0.82, 0)
TeleportWorldBtn.Size = UDim2.new(0.8, 0, 0, 42)
TeleportWorldBtn.Text = "الانتقال لمركز المرحلة (يم الوحش) ⚡"
TeleportWorldBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
TeleportWorldBtn.TextSize = 14
TeleportWorldBtn.Font = Enum.Font.SourceSansBold

TeleportWorldBtn.MouseButton1Click:Connect(function()
    local monsterTarget = nil
    
    -- 1. فحص مجسمات الوحوش والـ Bosses بالمركز
    for _, v in ipairs(workspace:GetDescendants()) do
        if v:IsA("Humanoid") and v.Parent and v.Parent ~= LocalPlayer.Character then
            local modelName = v.Parent.Name:lower()
            if modelName:find(selectedWorld:lower()) or modelName:find("boss") or modelName:find("monster") then
                local rootPart = v.Parent:FindFirstChild("HumanoidRootPart") or v.Parent:FindFirstChild("Torso") or v.Parent.PrimaryPart
                if rootPart then
                    monsterTarget = rootPart.CFrame
                    break
                end
            end
        end
    end
    
    -- 2. إذا لم يجد مجسم وحش مسمى، يبحث عن مركز أرضية المرحلة مباشرة
    if not monsterTarget then
        for _, v in ipairs(workspace:GetDescendants()) do
            if (v:IsA("TextLabel") and v.Text:lower():find(selectedWorld:lower())) or v.Name:lower() == selectedWorld:lower() then
                local parentPart = v:FindFirstAncestorWhichIsA("BasePart") or v.Parent
                if parentPart and parentPart:IsA("BasePart") then
                    -- الانتقال لأمام اللوحة نحو منتصف الساحة
                    monsterTarget = parentPart.CFrame * CFrame.new(0, 4, -25)
                    break
                end
            end
        end
    end
    
    if monsterTarget then
        forceTeleport(monsterTarget + Vector3.new(0, 3, 0))
    end
end)
